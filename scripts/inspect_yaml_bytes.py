from pathlib import Path
p=Path('.github/workflows/validate-csv.yml')
if not p.exists():
    print('file not found')
    raise SystemExit(1)
b=p.read_bytes()
lines=b.splitlines(True)
for i,line in enumerate(lines, start=1):
    print(f'LINE {i}: {line!r}')
    print('BYTES:', ' '.join(f"{c:02x}" for c in line))
    if i>=5:
        break
