# Operations

## First live dry run

Use the manual workflow before allowing publication.

1. Open the repository in GitHub.
2. Select **Actions**.
3. Select **Daily Blue Team Intelligence**.
4. Select **Run workflow**.
5. Keep the branch on the branch being tested.
6. Set `lookback_hours` to `24`.
7. Set `dry_run` to `true`.
8. Start the workflow.

A dry run performs live collection and writes report files inside the runner, but the publish job is skipped. It still uploads the complete `reports/` directory as a workflow artifact for inspection.

The workflow uses the built-in `GITHUB_TOKEN` for GitHub API access. An optional repository secret named `NVD_API_KEY` may be added to improve NVD API rate limits, but the pipeline is designed to work without it at a slower rate.

## Inspect the dry-run artifact

After the `collect` job completes:

1. Open the completed workflow run.
2. Confirm that **Install application**, **Run live collection**, **Validate generated reports**, and **Upload reports** succeeded.
3. Review the **Show source health** step.
4. Download the artifact named `reports-<RUN_ID>`.
5. Inspect at least:
   - `latest.md`
   - `latest.json`
   - `source-health.json`
   - the dated archive report
6. Confirm that live sources are marked `healthy`, `degraded`, `failed`, or `rate_limited` rather than `fixture_only`.
7. Confirm that fixture identifiers such as `CVE-2099-*`, `ExampleCorp`, and fixture URLs are absent.
8. Confirm that the coverage window is approximately the requested 24 hours.
9. Confirm that every selected item has a source-backed link and an explainable selection reason.

Do not enable publication when core sources fail or when the artifact contains fixture data.

## First publication run

Once the dry-run artifact has been reviewed:

1. Run **Daily Blue Team Intelligence** manually again.
2. Use `lookback_hours=24`.
3. Set `dry_run=false`.
4. Confirm the collection and validation jobs succeed.
5. Confirm the publish job commits only changed files under `reports/`.
6. Review the resulting commit and `reports/latest.md` on `main`.

Scheduled runs always use publication mode. They run daily at `06:17 UTC`.

## Publication quorum

Core quorum requires:

- CISA KEV; and
- at least one of NVD or GitHub Global Security Advisories.

A publishing run uses `--fail-on-degraded`, so failed core quorum blocks publication. EPSS, RSS, or defensive-release failures may degrade the report but do not independently define core quorum.

Manual dry runs deliberately do not use `--fail-on-degraded`, allowing the artifact and source-health diagnostics to be inspected even when one source is unavailable.

## Local verification

Create a virtual environment and install the package plus development tools:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install .
python -m pip install -r requirements-dev.txt
```

Run the test suite and deterministic fixture generation:

```bash
ruff check .
ruff format --check .
mypy src
pytest
python -m cyberdailylog run --offline-fixtures --output-dir tmp/reports
python -m cyberdailylog validate --output-dir tmp/reports
```

A local live test can then be run without publishing:

```bash
python -m cyberdailylog run --lookback-hours 24 --output-dir tmp/live-reports
python -m cyberdailylog validate --output-dir tmp/live-reports
```

Never commit API keys or local `.env` files.
