# Contributing

CyberDailyLog now accepts contributions to the Blue Team intelligence pipeline, fixtures, tests, source documentation, report rendering, and operational documentation.

Run locally with:

```bash
python -m pip install -r requirements.txt
ruff check .
ruff format --check .
mypy src
pytest
python -m cyberdailylog run --offline-fixtures --output-dir tmp/reports
python -m cyberdailylog validate --output-dir tmp/reports
```

Do not add personal diary features, hard-coded current CVE lists, random selection, certification-offer sections, exploit-code fetching, or application-level Git publishing.
