from pathlib import Path
from datetime import datetime, timezone
import json
import os
from urllib.parse import urlparse

from .settings import load_yaml
from .http import SafeHttpClient
from .models import Report
from .collectors.cisa_kev import CisaKevCollector
from .collectors.nvd import NvdCollector
from .collectors.epss import EpssCollector
from .collectors.github_advisories import GitHubAdvisoryCollector
from .collectors.vendor_advisories import VendorAdvisoryCollector
from .collectors.rss import RssCollector
from .collectors.github_releases import GitHubReleaseCollector
from .collectors.hacker_news import HackerNewsCollector
from .state import StateLedger, coverage_start, parse_date
from .operational_evidence import load_operational_evidence
from .source_health import quorum_ok
from .renderers.markdown import write_markdown
from .renderers.json import write_json, _atomic_write
from .telemetry import PipelineTiming


class Pipeline:
    def __init__(self, config_dir=Path("config"), output_dir=Path("reports"), offline=False):
        self.config_dir = Path(config_dir)
        self.output_dir = Path(output_dir)
        self.offline = offline
        self.sources = load_yaml(self.config_dir / "sources.yml")
        self.scoring = load_yaml(self.config_dir / "scoring.yml")
        self.report_config = load_yaml(self.config_dir / "report.yml")
        self.tech = load_yaml(self.config_dir / "technologies.yml")
        vendor_path = self.config_dir / "vendor-advisories.yml"
        self.vendor_advisories = load_yaml(vendor_path).get("advisories", []) if vendor_path.exists() else []
        hosts = {
            "www.cisa.gov",
            "services.nvd.nist.gov",
            "api.first.org",
            "api.github.com",
            "msrc.microsoft.com",
            "sec.cloudapps.cisco.com",
            "access.redhat.com",
            "ubuntu.com",
            "www.debian.org",
            "chromereleases.googleblog.com",
        }
        for source in self.sources.get("rss_sources", []):
            if source.get("enabled", True):
                host = urlparse(str(source.get("url") or "")).hostname
                if host:
                    hosts.add(host)
        hacker_news = self.sources.get("hacker_news", {})
        if hacker_news.get("enabled", False):
            host = urlparse(str(hacker_news.get("base_url") or "")).hostname
            if host:
                hosts.add(host)
        self.http = SafeHttpClient(hosts)

    def run(self, since=None, until=None, lookback_hours=24, dry_run=False, fail_on_degraded=False):
        self.timing = PipelineTiming()
        outcome = "failed"
        try:
            report = self._run(since, until, lookback_hours, dry_run, fail_on_degraded)
            outcome = (
                "fixture_only"
                if self.offline
                else "complete"
                if all(source.status == "healthy" for source in report.source_health)
                else "partial"
            )
            return report
        finally:
            self.timing.data["dry_run"] = dry_run
            _atomic_write(
                self.output_dir / "pipeline-metrics.json", json.dumps(self.timing.finish(outcome), indent=2) + "\n"
            )

    def _run(self, since, until, lookback_hours, dry_run, fail_on_degraded):
        until = until or datetime.now(timezone.utc).replace(microsecond=0)
        ledger = StateLedger(self.output_dir / "cti-state.json.gz")
        self.timing.mark("ledger_load")
        ledger.seed_archives(self.output_dir)
        previous_report_path = self.output_dir / "latest.json"
        if previous_report_path.exists():
            previous_report = json.loads(previous_report_path.read_text())
            previous_end = parse_date(previous_report.get("coverage_end"))
            ledger_end = parse_date(ledger.data.get("coverage_end"))
            incomplete = any(
                source.get("required") and source.get("status") not in {"healthy", "fixture_only"}
                for source in previous_report.get("source_health", [])
            )
            # Repair a watermark written by the first migration before partial
            # core failures were distinguished from complete coverage.
            if incomplete and previous_end and ledger_end and ledger_end >= previous_end:
                ledger.data["coverage_end"] = previous_report["coverage_start"]
        since = since or coverage_start(ledger, until, lookback_hours)
        previous_coverage = ledger.data.get("coverage_end") or since.isoformat()
        self.timing.data["baseline_records"] = len(ledger.records)
        self.timing.mark("prepare")
        rss_collectors = [
            RssCollector(self.http, offline=self.offline, sources=[source])
            for source in self.sources.get("rss_sources", [])
            if source.get("enabled", True)
        ]
        collectors = [
            CisaKevCollector(self.http, offline=self.offline),
            NvdCollector(self.http, offline=self.offline, token=os.getenv("NVD_API_KEY")),
            GitHubAdvisoryCollector(self.http, offline=self.offline, token=os.getenv("GITHUB_TOKEN")),
            *rss_collectors,
            GitHubReleaseCollector(
                self.http,
                offline=self.offline,
                token=os.getenv("GITHUB_TOKEN"),
                repos=self.sources.get("github_releases", []),
            ),
        ]
        hacker_news = self.sources.get("hacker_news", {})
        if hacker_news.get("enabled", False):
            collectors.append(HackerNewsCollector(self.http, offline=self.offline, config=hacker_news))
        # Independent, bounded public vendor evidence. Do not count this
        # optional source as a successful NVD bulk collection.
        if self.vendor_advisories and not self.offline:
            collectors.append(
                VendorAdvisoryCollector(self.http, token=os.getenv("GITHUB_TOKEN"), advisories=self.vendor_advisories)
            )

        items = load_operational_evidence(self.config_dir / "operational-evidence.yml")
        health = []
        self.timing.data["sources"] = {}
        for collector in collectors:
            before_http = dict(self.http.metrics)
            got, source_health = collector.collect(since, until)
            items += got
            health.append(source_health)
            self.timing.data["sources"][source_health.source] = {
                "status": source_health.status,
                "http_attempts": self.http.metrics["attempts"] - before_http["attempts"],
                "http_retries": self.http.metrics["retries"] - before_http["retries"],
                **getattr(collector, "metrics", {}),
            }
        self.timing.mark("collection")
        cves = sorted({cve for item in items for cve in item.cve_ids})
        before_http = dict(self.http.metrics)
        epss, epss_health = EpssCollector(self.http, offline=self.offline).collect_scores(cves)
        health.append(epss_health)
        self.timing.data["sources"][epss_health.source] = {
            "status": epss_health.status,
            "http_attempts": self.http.metrics["attempts"] - before_http["attempts"],
            "http_retries": self.http.metrics["retries"] - before_http["retries"],
        }
        for item in items:
            for cve in item.cve_ids:
                if cve in epss:
                    item.epss_score = float(epss[cve]["epss_score"])
                    item.epss_percentile = float(epss[cve]["epss_percentile"])
                    item.add_provenance("epss_score", "FIRST EPSS", item.epss_score)
        self.timing.mark("epss")
        if fail_on_degraded and not quorum_ok(health):
            raise SystemExit(2)
        for item in items:
            if any(cve in self.tech.get("confirmed_critical_asset_cves", []) for cve in item.cve_ids):
                item.critical_asset_exposure = True
        selected = ledger.observe(
            items, datetime.now(timezone.utc).replace(microsecond=0), since, until, self.tech, self.scoring
        )
        self.timing.mark("matching")
        # A quorum can publish useful partial coverage. Keep the catch-up
        # watermark until every core collector succeeds, so an NVD/GHSA
        # outage cannot permanently skip that source's modification window.
        if any(source.required and source.status not in {"healthy", "fixture_only"} for source in health):
            ledger.data["coverage_end"] = previous_coverage
        report = Report(
            generated_at=datetime.now(timezone.utc).replace(microsecond=0),
            coverage_start=since,
            coverage_end=until,
            degraded=not quorum_ok(health),
            items=selected,
            source_health=health,
            cti_summary={
                "new_vulnerabilities": sum(i.discovery_type == "new_vulnerability" for i in selected),
                "state_changes": sum(bool(i.transition_type) for i in selected),
                "kev_transitions": sum("entered_cisa_kev" in i.transition_type for i in selected),
                "ransomware_transitions": sum("ransomware_linked" in i.transition_type for i in selected),
                "tracked_vulnerabilities": len(ledger.records),
            },
        )
        if report.degraded and fail_on_degraded:
            raise SystemExit(2)
        write_markdown(report, self.output_dir, self.report_config)
        write_json(report, self.output_dir)
        self.timing.mark("render")
        if not dry_run and not report.degraded:
            ledger.save()
        self.timing.mark("ledger_write")
        self.timing.data.update(
            tracked_records=len(ledger.records),
            report_generated=report.generated_at.isoformat(),
            ledger_bytes=ledger.path.stat().st_size if ledger.path.exists() else None,
        )
        return report
