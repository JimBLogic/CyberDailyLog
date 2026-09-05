#!/usr/bin/env bash
set -euo pipefail
bash scripts/sites-env.sh -- wrangler types .sites-runtime/cloudflare-runtime.d.ts --config dist/server/wrangler.json --include-env false
bash scripts/sites-env.sh -- tsc --noEmit
