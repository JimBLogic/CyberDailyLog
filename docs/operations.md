# Operations

## First live dry run

1. Open **Actions** in GitHub.
2. Select the `Daily Blue Team Intelligence` workflow.
3. Select the current `main` branch.
4. Set `lookback_hours=24`.
5. Keep `dry_run=true`.
6. Run the workflow.

A workflow dry run performs live collection and writes real reports, but it does not commit or publish them. Do not treat the workflow as production-proven until a post-merge `dry_run=true` run on `main` has produced and uploaded real reports successfully.

## Artifact inspection

Download the workflow artifact named `reports-<RUN_ID>` from the completed Actions run. Inspect at least:

- `latest.md`;
- `latest.json`;
- `source-health.json`;
- the dated archive files under `archive/<YEAR>/<MONTH>/`.

Before publication, check:

- source statuses in `source-health.json`;
- the coverage window in `latest.json` and `latest.md`;
- that selected items include source-backed links;
- selection reasons for the top items;
- absence of fixture identifiers from live output;
- absence of placeholder domains;
- no unexpected secrets, API keys or tokens in any report file.

## First publication

After a successful dry-run inspection:

1. Rerun the workflow from `main`.
2. Set `dry_run=false`.
3. Confirm the run reaches publication only if source quorum succeeds.
4. Review the generated commit.
5. Confirm the commit changed only `reports/` files.

The workflow uses the built-in `GITHUB_TOKEN`; no personal access token is required.

## Quorum behavior

Publication is guarded by source quorum:

- CISA KEV is required.
- At least one of NVD or GitHub Advisories is required.
- Optional-source failures, such as EPSS, RSS or GitHub release collection failures, may degrade the report.
- Dry runs permit diagnostic artifacts even when core quorum is degraded.
- Publication runs use `--fail-on-degraded` and block before publication when core quorum fails.

## Local verification

Use Python 3.12 or newer. Install the application and development tooling separately:

```bash
python -m pip install --upgrade pip
python -m pip install .
python -m pip install -r requirements-dev.txt
```

Run the full local verification matrix without `PYTHONPATH=src`:

```bash
ruff check .
ruff format --check .
mypy src
pytest
python -m cyberdailylog run --offline-fixtures --output-dir tmp/reports
python -m cyberdailylog validate --output-dir tmp/reports
python -m cyberdailylog run --offline-fixtures --since 2026-07-15T00:00:00 --until 2026-07-16T00:00:00Z --output-dir tmp/datetime-reports
python -m cyberdailylog validate --output-dir tmp/datetime-reports
python -m pip_audit -r requirements.txt -r requirements-dev.txt
git diff --check
```

The scheduled daily workflow installs only the runtime package with `python -m pip install .`; CI installs both the runtime package and pinned development tools.
