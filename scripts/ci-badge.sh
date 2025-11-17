#!/usr/bin/env bash
set -euo pipefail

WORKFLOW_FILE=${1:-validate-csv.yml}
README_FILE="README.md"

python - "$WORKFLOW_FILE" "$README_FILE" <<'PY'
import re
import sys
from pathlib import Path

workflow = sys.argv[1]
readme = Path(sys.argv[2])
text = readme.read_text()
pattern = r"https://github\.com/JimBLogic/CyberDailyLog/actions/workflows/[^/]+/badge\.svg"
replacement = f"https://github.com/JimBLogic/CyberDailyLog/actions/workflows/{workflow}/badge.svg"
new = re.sub(pattern, replacement, text)
if new == text:
    print(f"README badge already using {workflow}")
else:
    readme.write_text(new)
    print(f"Updated README badge to {replacement}")
PY
