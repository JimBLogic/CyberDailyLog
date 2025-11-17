# Changelog

All notable changes to this project will be documented in this file.

## [1.1.1] - 2025-11-17

### Added
- **CYBER_INTEL_LATEST.md**: Separated intel report from README to prevent merge conflicts
- **CONTRIBUTING.md**: Comprehensive contribution guidelines with setup instructions
- Executable permissions for all shell scripts (.sh files) using `git update-index`
- `.pre-commit-config.yaml`: Local pre-commit hook that runs `scripts/validate_csv.py`
- `scripts/archive.sh`: Appends the latest report to `cyber-intel-archive.md` and keeps the last 30 days
- `scripts/normalize_dates.py`: Extracted date normalization helper for reuse
- `scripts/ci-badge.sh`: Updates the README badge URL when workflow filenames change
- `scripts/coverage.sh`: Runs `pytest` with coverage reporting for the validator

### Changed
- **README.md**: Now links to CYBER_INTEL_LATEST.md instead of embedding full report
- **fetch-news.ps1**: Updated to write to CYBER_INTEL_LATEST.md instead of README
- Improved Contributing section in README with link to detailed guide

### Fixed
- Shell scripts now have proper executable permissions for Unix-like systems
- Intel report separation eliminates frequent README churn
- Cleaner repository history with dynamic data isolated from documentation

## [1.0.0] - 2025-11-17

### Added
- CSV validator with automatic date normalization (8 formats supported)
- Pre-commit hooks for PowerShell 7 and Windows PowerShell
- GitHub Actions CI workflow with pytest and PR commenting
- Cross-platform hook installers (PowerShell and Bash)
- Unit test suite with 3 passing tests
- Makefile for automation (install-hooks, validate-csv)
- Comprehensive .gitignore covering Python, OS files, and build artifacts
- MIT License
- CI badge in README

### Features
- **Date Normalization**: Auto-converts MM/DD/YYYY, DD-MM-YYYY, etc. to ISO-8601
- **BOM Handling**: Strips UTF-8 BOM automatically
- **Auto-Header**: Inserts header if missing
- **4-Column Validation**: Ensures proper CSV structure
- **Empty Field Detection**: Catches incomplete entries
- **CI Integration**: Validates on every push, comments on PRs with errors
