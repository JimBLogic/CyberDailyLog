# Current state audit

Audit performed before modification on 2026-07-15.

## Problems found

- `README.md` advertised a personal daily log and embedded a stale latest summary with free certifications and static CVEs.
- `daily-log.csv` was an active personal-progress artifact; it is now preserved under `legacy/personal-progress/` only.
- `CYBER_INTEL_LATEST.md`, `cyber-intel-archive.md`, and `.cyber-intel-history.json` represented a static intelligence v1 design and are preserved under `legacy/static-intel-v1/`.
- `scripts/fetch-news.sh` and `scripts/fetch-news.ps1` duplicated business logic, contained hard-coded certification offers and CVEs, selected entries randomly, and ran `git commit` plus `git push` themselves.
- `scripts/archive.sh` maintained one append-only Markdown archive that was difficult to query.
- `scripts/validate_csv.py` and related tests made CSV diary validation the primary feature.
- `.githooks/` and `.pre-commit-config.yaml` focused on CSV validation.
- `.github/workflows/daily-news.yml` required `custom GitHub personal access token`, delegated publishing to the script, and still validated the CSV.
- `.github/workflows/validate-csv.yml` suppressed validator failures by using `|| true` before reading the exit status.
- The old Markdown reports did not show source health or distinguish collected, published, and modified timestamps.

## Corrections made

The active project now uses one Python package for collection, correlation, scoring, rendering, validation, and source health. Personal diary files and static intelligence v1 files are moved to `legacy/`, old workflows/scripts are removed, and new CI/daily workflows use the built-in `GITHUB_TOKEN`.
