#!/usr/bin/env bash
set -euo pipefail

ARCHIVE_FILE="cyber-intel-archive.md"
LATEST_FILE="CYBER_INTEL_LATEST.md"
KEEP_DAYS=${1:-30}

if [[ ! -f "$LATEST_FILE" ]]; then
  echo "Latest report ($LATEST_FILE) not found" >&2
  exit 1
fi

if [[ ! -f "$ARCHIVE_FILE" ]]; then
  cat <<'EOF' > "$ARCHIVE_FILE"
# Cyber Intelligence Archive

> Historical daily reports
EOF
fi

ENTRY_DATE=$(date +%F)
{
  printf "\n---\n\n## %s\n\n" "$ENTRY_DATE"
  cat "$LATEST_FILE"
  printf "\n"
} >> "$ARCHIVE_FILE"

python - <<PY
import sys
from pathlib import Path
archive = Path(sys.argv[1])
keep = int(sys.argv[2])
text = archive.read_text(encoding='utf-8').strip()
if not text:
    sys.exit(0)
parts = text.split('\n---\n\n')
header = parts[0]
entries = parts[1:]
if len(entries) <= keep:
    sys.exit(0)
kept = entries[-keep:]
body = '\n---\n\n'.join(kept)
archive.write_text(header + '\n---\n\n' + body + '\n', encoding='utf-8')
PY
