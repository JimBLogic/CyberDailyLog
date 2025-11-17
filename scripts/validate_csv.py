#!/usr/bin/env python3
"""Robust validator and normalizer for `daily-log.csv`.

Exports functions so unit tests can import behavior.
"""
from pathlib import Path
from datetime import datetime
import sys
from typing import List, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.normalize_dates import normalize_date


DEFAULT_HEADER = 'date,pillar,task,notes'
EXPECTED_HEADER = [h.strip().lower() for h in DEFAULT_HEADER.split(',')]


def strip_bom_and_read(path: Path) -> List[str]:
    raw = path.read_text(encoding='utf-8')
    if raw.startswith('\ufeff'):
        raw = raw.lstrip('\ufeff')
    return raw.splitlines()


def find_first_nonempty(lines: List[str]):
    for i, l in enumerate(lines):
        if l.strip() != '':
            return i, l
    return None


def looks_like_date(s: str) -> bool:
    s = s.strip()
    try:
        datetime.strptime(s, '%Y-%m-%d')
        return True
    except Exception:
        return False


def validate_and_normalize(path: Path) -> Tuple[int, List[str], bool]:
    """Validate and optionally normalize `daily-log.csv`.

    Returns (exit_code, messages, modified) where exit_code is 0 for OK,
    2 for validation errors, 1 for missing file. messages is a list of lines
    describing actions/errors. modified is True when the file was written.
    """
    if not path.exists():
        return 1, ['daily-log.csv not found'], False

    lines = strip_bom_and_read(path)
    first_non = find_first_nonempty(lines)
    messages: List[str] = []
    modified = False

    if first_non is None:
        # empty file -> write header
        path.write_text(DEFAULT_HEADER + '\n', encoding='utf-8')
        messages.append('daily-log.csv was empty; header added')
        return 0, messages, True

    idx, hdr_candidate = first_non
    has_header = [h.strip().lower() for h in hdr_candidate.split(',')] == EXPECTED_HEADER

    # header missing but first row looks like data -> insert header
    if not has_header and looks_like_date(hdr_candidate.split(',')[0]):
        lines.insert(0, DEFAULT_HEADER)
        path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
        messages.append('Header was missing; prepended header to daily-log.csv')
        modified = True
        # recompute start index
        start = 1
    else:
        # header is at the first non-empty index
            start = idx + 1 if has_header else idx

    errors = 0
    # Normalize dates in-place, collect changes
    for i in range(start, len(lines)):
        lineno = i + 1
        line = lines[i]
        if line.strip() == '':
            continue
        parts = [p.strip() for p in line.split(',')]
        if len(parts) != 4:
            messages.append(f'Invalid CSV line {lineno}: expected 4 columns, found {len(parts)}')
            errors += 1
            continue
        date_s, pillar, task, notes = parts
        norm_date, changed = normalize_date(date_s)
        if changed:
            lines[i] = ','.join([norm_date, pillar, task, notes])
            modified = True
            messages.append(f'Normalized date at line {lineno}: "{date_s}" -> "{norm_date}"')
        # validate normalized date
        try:
            datetime.strptime(lines[i].split(',')[0].strip(), '%Y-%m-%d')
        except Exception:
            messages.append(f'Invalid date at line {lineno}: "{date_s}" (expected YYYY-MM-DD)')
            errors += 1
        if pillar == '':
            messages.append(f'Empty pillar at line {lineno}')
            errors += 1
        if task == '':
            messages.append(f'Empty task at line {lineno}')
            errors += 1

    if modified:
        path.write_text('\n'.join(lines) + '\n', encoding='utf-8')

    if errors:
        return 2, messages, modified
    messages.append('daily-log.csv OK' + (' (modified)' if modified else ''))
    return 0, messages, modified


def main():
    path = Path('daily-log.csv')
    code, messages, modified = validate_and_normalize(path)
    for m in messages:
        print(m)
    sys.exit(code)


if __name__ == '__main__':
    main()
