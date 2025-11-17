from pathlib import Path
p = Path('daily-log.csv')
if not p.exists():
    print('MISSING')
    raise SystemExit(1)
data = p.read_text(encoding='utf-8')
if data == '':
    print('<EMPTY FILE>')
    raise SystemExit(0)
for i, line in enumerate(data.splitlines(), start=1):
    print(f'LINE {i}: {line!r}')
