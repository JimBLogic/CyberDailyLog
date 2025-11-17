# Contributing to CyberDailyLog

Thank you for considering a contribution! Please follow these steps:

## 1️⃣ Clone & Set Up
```bash
git clone https://github.com/JimBLogic/CyberDailyLog.git
cd CyberDailyLog
python3 -m venv .venv
source .venv/bin/activate   # or .\.venv\Scripts\activate on Windows
pip install -r scripts/requirements.txt
```

## 2️⃣ Install Git Hooks
```bash
make install-hooks   # or ./scripts/install-githooks.sh (Linux/macOS) / ./scripts/install-githooks.ps1 (Windows)
```

## 3️⃣ Make Changes
- Keep `daily-log.csv` in the format `date,pillar,task,notes` (ISO‑8601 dates).
- Run `make validate-csv` locally to ensure the CSV passes validation.
- Supported date formats are automatically normalized to `YYYY-MM-DD`.

## 4️⃣ Run Tests
```bash
pytest -q
```

## 5️⃣ Commit & Push
```bash
git add .
git commit -m "Your concise description"
git push origin your-branch
```

## 6️⃣ Open a Pull Request
The CI workflow will automatically run the validator and tests. Once the checks pass, a reviewer will merge your changes.

---

## 📋 Project Structure

- `daily-log.csv` - Personal achievement tracker (4 columns: date, pillar, task, notes)
- `scripts/validate_csv.py` - CSV validator with date normalization (8 formats)
- `scripts/fetch-news.ps1` - Daily cyber intelligence automation (certs + CVEs)
- `.githooks/pre-commit` - Pre-commit hook that validates CSV before each commit
- `CYBER_INTEL_LATEST.md` - Always-current intelligence report (updated daily)
- `cyber-intel-archive.md` - Historical archive of all past reports

## 🛠️ Available Commands

| Command | Description |
|---------|-------------|
| `make install-hooks` | Install Git pre-commit hooks |
| `make validate-csv` | Validate `daily-log.csv` format |
| `pytest -q` | Run all unit tests |
| `./scripts/fetch-news.ps1` | Generate daily cyber intelligence report |

## 📝 CSV Format Requirements

- **4 columns:** date, pillar, task, notes
- **Date format:** ISO-8601 (YYYY-MM-DD) - auto-normalized from 8 formats
- **No empty fields:** All columns must have values
- **UTF-8 encoding:** BOM automatically stripped if present

## 🐛 Reporting Issues

Found a bug? Have a feature request? Please [open an issue](https://github.com/JimBLogic/CyberDailyLog/issues) with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System info (OS, Python version)

---

Need help? Open an issue or ping the repository maintainer. Happy hacking! 🚀
