#!/usr/bin/env python3
"""Validate daily-log.csv: every non-empty line must have exactly 4 comma-separated columns."""
import sys
from pathlib import Path

path = Path('daily-log.csv')
if not path.exists():
    print('daily-log.csv not found', file=sys.stderr)
    sys.exit(1)

errors = 0
with path.open(encoding='utf-8') as f:
    for i, line in enumerate(f, start=1):
        line = line.rstrip('\n')
        if not line.strip():
            continue
        parts = line.split(',')
        if len(parts) != 4:
            print(f'Invalid CSV line {i}: expected 4 columns, found {len(parts)}', file=sys.stderr)
            errors += 1

if errors:
    sys.exit(2)

print('daily-log.csv OK')
sys.exit(0)
