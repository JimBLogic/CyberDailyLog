#!/usr/bin/env python3
"""Validate `daily-log.csv`.

This script:
- strips a leading UTF-8 BOM if present
- inserts a header row if the file is empty or if it appears to be missing a header
- validates each data row has 4 columns, a date in YYYY-MM-DD, and non-empty pillar/task

Exit codes:
  0 - OK (maybe after auto-fix)
  1 - file missing
  2 - validation errors
"""
from pathlib import Path
from datetime import datetime
import sys

path = Path('daily-log.csv')
if not path.exists():
    print('daily-log.csv not found', file=sys.stderr)
    sys.exit(1)

# Read and normalize (strip BOM)
raw = path.read_text(encoding='utf-8')
if raw.startswith('\ufeff'):
    raw = raw.lstrip('\ufeff')
lines = raw.splitlines()

def is_blank(s):
    return s.strip() == ''

# find first non-empty
first_non = None
for i, l in enumerate(lines):
    if not is_blank(l):
        first_non = (i, l)
        break

# if empty -> write header
header = 'date,pillar,task,notes'
if first_non is None:
    path.write_text(header + '\n', encoding='utf-8')
    print('daily-log.csv was empty; header added')
    sys.exit(0)

hdr_candidate = first_non[1].strip()
expected_header = [h.strip().lower() for h in header.split(',')]
has_header = ([h.strip().lower() for h in hdr_candidate.split(',')] == expected_header)

# if first data row looks date-like and there's no header, prepend header
date_like = False
cols0 = hdr_candidate.split(',')
if len(cols0) >= 1:
    try:
        datetime.strptime(cols0[0].strip(), '%Y-%m-%d')
        date_like = True
    except Exception:
        date_like = False

modified = False
if not has_header and date_like:
    lines.insert(0, header)
    path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    modified = True
    print('Header was missing; prepended header to daily-log.csv')

# determine start index (row after header)
if has_header:
    start = first_non[0] + 1
elif modified:
    # header inserted at index 0
    start = 1
else:
    # No header and we didn't modify; treat first non-empty as header if it had 4 cols
    if len(hdr_candidate.split(',')) == 4:
        start = first_non[0] + 1
    else:
        print('Unable to determine header in daily-log.csv', file=sys.stderr)
        sys.exit(2)

errors = 0
for idx in range(start, len(lines)):
    lineno = idx + 1
    line = lines[idx]
    if is_blank(line):
        continue
    parts = [p.strip() for p in line.split(',')]
    if len(parts) != 4:
        print(f'Invalid CSV line {lineno}: expected 4 columns, found {len(parts)}', file=sys.stderr)
        errors += 1
        continue
    date_s, pillar, task, notes = parts
    # date
    try:
        datetime.strptime(date_s, '%Y-%m-%d')
    except Exception:
        print(f'Invalid date at line {lineno}: "{date_s}" (expected YYYY-MM-DD)', file=sys.stderr)
        errors += 1
    if pillar == '':
        print(f'Empty pillar at line {lineno}', file=sys.stderr)
        errors += 1
    if task == '':
        print(f'Empty task at line {lineno}', file=sys.stderr)
        errors += 1

if errors:
    sys.exit(2)

if modified:
    print('daily-log.csv OK (header inserted)')
else:
    print('daily-log.csv OK')
sys.exit(0)
