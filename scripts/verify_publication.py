"""Verify a complete artifact and preserve the published ledger before commit.

Only stdlib: the main-only publisher does not install application dependencies.
The manifest is transport integrity, not a signature or a replacement for CI trust.
"""

import argparse
from datetime import datetime
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo

MAX_STATE_BYTES = 512 * 1024 * 1024
MANIFEST = "publication-manifest.json"


def stamp(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("Publication timestamps must have an explicit timezone")
    return result


def decode_state(raw):
    import io

    if len(raw) > 48 * 1024 * 1024:
        raise ValueError("Ledger exceeds compressed budget")
    with gzip.GzipFile(fileobj=io.BytesIO(raw)) as stream:
        decoded = stream.read(MAX_STATE_BYTES + 1)
    if len(decoded) > MAX_STATE_BYTES:
        raise ValueError("Ledger exceeds decoded budget")
    state = json.loads(decoded)
    if state.get("schema_version") != 2 or not isinstance(state.get("vulnerabilities"), dict):
        raise ValueError("Invalid ledger schema")
    return state


def preserve_history(previous, candidate):
    before, after = previous["vulnerabilities"], candidate["vulnerabilities"]
    if not before.keys() <= after.keys():
        raise ValueError("Publication would discard historical CVEs")
    for cve, record in before.items():
        newer = after[cve]
        if record["first_seen"] != newer["first_seen"]:
            raise ValueError("Publication would rewrite first_seen")
        if not record["observations"].keys() <= newer["observations"].keys():
            raise ValueError("Publication would discard source observations")
        transitions = record["transitions"]
        if transitions != newer["transitions"][: len(transitions)]:
            raise ValueError("Publication would rewrite transition history")
        for source, snapshot in record["observations"].items():
            old = snapshot.get("modified_at")
            new = newer["observations"][source].get("modified_at")
            if old and (not new or stamp(old) > stamp(new)):
                raise ValueError("Publication would regress a source observation")
    if previous.get("coverage_end") and (
        not candidate.get("coverage_end") or stamp(previous["coverage_end"]) > stamp(candidate["coverage_end"])
    ):
        raise ValueError("Publication would regress the coverage watermark")
    return {"baseline_cves": len(before), "candidate_cves": len(after), "history_preserved": True}


def bundle(root):
    def read(name):
        return json.loads((root / "reports" / name).read_text())

    report = read("latest.json")
    generated = report["generated_at"]
    stamp(generated)
    date = stamp(report["coverage_end"]).date().isoformat()
    folder = "reports/archive/" + date[:4] + "/" + date[5:7] + "/" + date
    required = {
        "README.md",
        "reports/latest.json",
        "reports/latest.md",
        "reports/source-health.json",
        "reports/portfolio-feed.json",
        "reports/dashboard-feed.json",
        "reports/cti-state.json.gz",
        "reports/pipeline-metrics.json",
        folder + ".json",
        folder + ".md",
        folder + "-source-health.json",
    }
    names = {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and p.relative_to(root).as_posix() != MANIFEST
    }
    if names != required or any(p.is_symlink() for p in root.rglob("*")):
        raise ValueError("Incomplete or unexpected publication artifact files")
    if report.get("degraded") is not False or not isinstance(report.get("items"), list):
        raise ValueError("Invalid or degraded publication artifact")
    for name in ("portfolio-feed.json", "dashboard-feed.json"):
        feed = read(name)
        if feed.get("generated_at") != generated or feed.get("project") != "CyberDailyLog":
            raise ValueError("Mixed generation timestamps in publication feeds")
    if read("source-health.json") != report["source_health"]:
        raise ValueError("Mixed source health in publication bundle")
    if read("pipeline-metrics.json").get("report_generated") != generated:
        raise ValueError("Metrics do not belong to this report")
    for name, suffix in (("latest.json", ".json"), ("latest.md", ".md"), ("source-health.json", "-source-health.json")):
        if (root / "reports" / name).read_bytes() != (root / (folder + suffix)).read_bytes():
            raise ValueError("Archive and current report are inconsistent")
    hashes = {name: hashlib.sha256((root / name).read_bytes()).hexdigest() for name in sorted(required)}
    return {"schema_version": 1, "generated_at": generated, "files": hashes}, report


def daily_close(report):
    if report.get("degraded") is not False:
        return None
    healthy = {s["source"] for s in report.get("source_health", []) if s.get("status") == "healthy"}
    local = stamp(report["generated_at"]).astimezone(ZoneInfo("Europe/Madrid"))
    return (
        local.date().isoformat() if local.hour >= 12 and {"cisa_kev", "nvd", "github_advisories"} <= healthy else None
    )


def git_file(ref, path):
    result = subprocess.run(["git", "show", f"{ref}:{path}"], capture_output=True)
    if result.returncode:
        # Missing baseline is allowed only for a repository's initial migration.
        if subprocess.run(["git", "cat-file", "-e", ref], capture_output=True).returncode:
            raise ValueError("Unresolvable publication baseline")
        return None
    return result.stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--baseline-ref")
    parser.add_argument("--evidence", type=Path)
    args = parser.parse_args()
    manifest, report = bundle(args.root)
    target = args.root / MANIFEST
    if args.write_manifest:
        target.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
        return 0
    if json.loads(target.read_text()) != manifest:
        raise ValueError("Publication manifest integrity mismatch")
    candidate = decode_state((args.root / "reports/cti-state.json.gz").read_bytes())
    evidence = {"bundle_verified": True, "candidate_cves": len(candidate["vulnerabilities"]), "duplicate_close": False}
    if args.baseline_ref:
        raw_report = git_file(args.baseline_ref, "reports/latest.json")
        if raw_report:
            previous_report = json.loads(raw_report)
            previous_close = daily_close(previous_report)
            candidate_day = stamp(report["generated_at"]).astimezone(ZoneInfo("Europe/Madrid")).date().isoformat()
            evidence["duplicate_close"] = bool(previous_close and previous_close == candidate_day)
            if evidence["duplicate_close"]:
                evidence["baseline_unchanged"] = True
                if args.evidence:
                    args.evidence.write_text(json.dumps(evidence, indent=2) + "\n")
                print(json.dumps(evidence, sort_keys=True))
                return 0
            if stamp(previous_report["generated_at"]) > stamp(report["generated_at"]):
                raise ValueError("Stale artifact would replace a newer publication")
        previous = git_file(args.baseline_ref, "reports/cti-state.json.gz")
        if not previous:
            raise ValueError("Published ledger is missing; refusing to create a replacement baseline")
        evidence.update(preserve_history(decode_state(previous), candidate))
    if args.evidence:
        args.evidence.write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps(evidence, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
