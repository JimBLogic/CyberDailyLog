# Scripts Directory

Helper scripts for CyberDailyLog repository.

## Validation & Testing

### `validate_csv.py`
**Purpose**: Validates `daily-log.csv` format and normalizes dates.

**Features**:
- Validates 4-column structure (date, pillar, task, notes)
- Auto-normalizes dates from 8 formats to ISO-8601 (YYYY-MM-DD)
- Strips UTF-8 BOM if present
- Auto-inserts header if missing
- Detects empty fields and invalid dates

**Usage**:
```powershell
python scripts/validate_csv.py
```

**Exit codes**:
- `0`: CSV is valid (may have auto-fixed issues)
- `1`: CSV has errors that couldn't be fixed

### `tests/test_validate_csv.py`
**Purpose**: Pytest unit tests for the validator.

**Tests**:
- Empty file handling
- Date normalization (11/17/2025 → 2025-11-17)
- Invalid row detection

**Usage**:
```powershell
pytest -q
```

## Automation Scripts

### `fetch-news.ps1` / `fetch-news.sh`
**Purpose**: Automated daily cyber intelligence report generator.

**Features**:
- Fetches 3 random free certification offers (Google Cloud, Cisco, AWS, Azure, Palo Alto)
- Fetches 3 random high-severity CVEs (CVSS ≥ 7.5)
- Creates formatted markdown report: `cyber-intel-YYYY-MM-DD.md`
- Auto-commits and pushes to GitHub
- Keeps news separate from personal daily-log.csv

**Usage (PowerShell)**:
```powershell
./scripts/fetch-news.ps1
```

**Usage (Bash/WSL)**:
```bash
chmod +x scripts/fetch-news.sh
./scripts/fetch-news.sh
```

**Scheduling**:
- **Windows**: Task Scheduler at 08:00 daily
- **Linux/macOS**: Cron job `0 8 * * 1-5`
- **GitHub Actions**: `.github/workflows/daily-news.yml` (runs at 08:00 EST weekdays)

**Output**: Creates markdown file:
```markdown
# Cyber Intelligence Report - 2025-11-17

## 🎓 Free Cloud & Security Certifications
1. Google Cloud Cybersecurity Certificate...
2. AWS re/Start...
3. Microsoft Azure Fundamentals...

## 🔴 Critical CVEs (CVSS ≥ 7.5)
1. CVE-2025-30397 - Edge scripting engine...
2. CVE-2025-32709 - WinSock driver...
3. CVE-2025-29813 - Azure DevOps Server...
```

## Utility Scripts

### `logwin.sh`
**Purpose**: Quick-add entries from command line (Bash/WSL/Git Bash).

**Usage**:
```bash
./scripts/logwin.sh Automation "Setup CI" "Configured GitHub Actions"
```

Appends: `2025-11-17,Automation,Setup CI,Configured GitHub Actions`

### `print_csv.py`
**Purpose**: Debug helper - prints CSV with line numbers and BOM detection.

**Usage**:
```powershell
python scripts/print_csv.py
```

**Output**:
```
LINE 1: '\ufeffdate,pillar,task,notes'  # Shows BOM if present
LINE 2: '2025-11-17,Automation,...'
```

### `inspect_yaml_bytes.py`
**Purpose**: Debug YAML encoding issues (used during workflow troubleshooting).

**Usage**:
```powershell
python scripts/inspect_yaml_bytes.py .github/workflows/csv-to-md.yml
```

## Hook Installers

### `install-githooks.ps1`
**Purpose**: Windows hook installer with pwsh/powershell detection.

**Usage**:
```powershell
./scripts/install-githooks.ps1
```

**What it does**:
1. Detects PowerShell 7 (pwsh) vs Windows PowerShell
2. Copies appropriate hook to `.githooks/pre-commit`
3. Runs `git config core.hooksPath .githooks`

### `install-githooks.sh`
**Purpose**: Unix/WSL/Git Bash hook installer.

**Usage**:
```bash
./scripts/install-githooks.sh
```

**What it does**:
1. Detects pwsh/powershell availability
2. Sets executable permissions (chmod +x)
3. Configures Git hooks path

## Development

### Adding New Scripts
1. Add script to `scripts/` directory
2. Document in this README
3. Add tests in `scripts/tests/` if applicable
4. Update `requirements.txt` if new dependencies needed

### Running All Tests
```powershell
pytest -q                           # Run test suite
python scripts/validate_csv.py       # Validate CSV
```
