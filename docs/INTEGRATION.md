# CyberDailyLog integration guide

CyberDailyLog publishes read-only static files from the `main` branch. Consumers do not need an API key.

## Endpoints

| Purpose | URL |
| --- | --- |
| Compact feed | `https://raw.githubusercontent.com/JimBLogic/CyberDailyLog/main/reports/portfolio-feed.json` |
| Compact-feed schema | `https://raw.githubusercontent.com/JimBLogic/CyberDailyLog/main/schemas/portfolio-feed.schema.json` |
| Complete report | `https://raw.githubusercontent.com/JimBLogic/CyberDailyLog/main/reports/latest.json` |
| Source health | `https://raw.githubusercontent.com/JimBLogic/CyberDailyLog/main/reports/source-health.json` |
| Human brief | `https://github.com/JimBLogic/CyberDailyLog/blob/main/reports/latest.md` |

`portfolio-feed.json` is the recommended interface for websites and other repositories. The complete report may be much larger. The feed exposes the same contract URL in `schema_url` and `endpoints.schema` so consumers can discover it without hard-coding a second path.

## Compact-feed contract

The feed keeps `schema_version: 1` for backward compatibility and includes:

- coverage and generation timestamps;
- pipeline status and source-health totals;
- number of qualified and above-threshold developments;
- immediate-attention count and summary;
- up to five ranked vulnerabilities;
- priority, CVSS, EPSS, exploitation and defensive-action fields;
- canonical links to the other outputs.

Consumers should ignore unknown fields and reject unsupported major schema versions.

## Strict JSON Schema validation

The public Draft 2020-12 schema validates required fields, timestamps, URLs, score ranges and the compact vulnerability records while still allowing backward-compatible additive fields.

```python
import json
from urllib.request import urlopen

from jsonschema import Draft202012Validator, FormatChecker

feed_url = "https://raw.githubusercontent.com/JimBLogic/CyberDailyLog/main/reports/portfolio-feed.json"
schema_url = "https://raw.githubusercontent.com/JimBLogic/CyberDailyLog/main/schemas/portfolio-feed.schema.json"

with urlopen(feed_url, timeout=15) as response:
    feed = json.load(response)
with urlopen(schema_url, timeout=15) as response:
    schema = json.load(response)

Draft202012Validator(schema, format_checker=FormatChecker()).validate(feed)
```

## Browser JavaScript

```javascript
const url =
  "https://raw.githubusercontent.com/JimBLogic/CyberDailyLog/main/reports/portfolio-feed.json";

const response = await fetch(url, { cache: "no-store" });
if (!response.ok) {
  throw new Error(`CyberDailyLog returned HTTP ${response.status}`);
}

const feed = await response.json();
if (feed.schema_version !== 1) {
  throw new Error(`Unsupported schema version: ${feed.schema_version}`);
}

const generatedAt = new Date(feed.generated_at);
const ageHours = (Date.now() - generatedAt.getTime()) / 3_600_000;
if (ageHours > 36) {
  console.warn("CyberDailyLog data is stale");
}

console.table(feed.top_vulnerabilities);
```

## Python

```python
import json
from datetime import datetime, timezone
from urllib.request import Request, urlopen

URL = (
    "https://raw.githubusercontent.com/JimBLogic/"
    "CyberDailyLog/main/reports/portfolio-feed.json"
)

request = Request(URL, headers={"User-Agent": "my-defensive-dashboard/1.0"})
with urlopen(request, timeout=15) as response:
    feed = json.load(response)

if feed["schema_version"] != 1:
    raise RuntimeError("Unsupported CyberDailyLog schema")

generated = datetime.fromisoformat(feed["generated_at"].replace("Z", "+00:00"))
age = datetime.now(timezone.utc) - generated.astimezone(timezone.utc)
if age.total_seconds() > 36 * 3600:
    raise RuntimeError("CyberDailyLog feed is stale")

for item in feed["top_vulnerabilities"]:
    print(item["id"], item["priority_score"], item["source_url"])
```

## curl

```bash
curl --fail --silent --show-error \
  https://raw.githubusercontent.com/JimBLogic/CyberDailyLog/main/reports/portfolio-feed.json
```

## GitHub Actions consumer

```yaml
name: Refresh CyberDailyLog data

on:
  schedule:
    - cron: "45 8 * * *"
  workflow_dispatch:

permissions:
  contents: read

jobs:
  fetch:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
      - name: Download compact feed
        run: |
          curl --fail --silent --show-error \
            --output cyberdailylog-feed.json \
            https://raw.githubusercontent.com/JimBLogic/CyberDailyLog/main/reports/portfolio-feed.json
      - name: Validate basic contract
        run: |
          python - <<'PY'
          import json
          from pathlib import Path

          feed = json.loads(Path("cyberdailylog-feed.json").read_text())
          assert feed["schema_version"] == 1
          assert isinstance(feed["top_vulnerabilities"], list)
          assert len(feed["top_vulnerabilities"]) <= 5
          PY
```

## Caching and failure handling

- Refresh after the repository's scheduled publication window.
- Treat data older than 36 hours as stale.
- Keep the last known valid feed when a refresh fails.
- Do not execute text or links received from the feed.
- Use `source_health` to distinguish required-source failure from optional-source degradation.
- Attribute CyberDailyLog and preserve official source links.

## Requesting changes or new sources

Open a reviewed pull request or issue in the repository. External systems must not inject unreviewed intelligence directly into the published feed.
