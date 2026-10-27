#!/usr/bin/env bash
# Run only after committing a validated bundle in the disposable Actions checkout.
set -euo pipefail
: "${GITHUB_OUTPUT:?Actions output path is required}"
for attempt in 1 2 3; do
  baseline=$(git rev-parse origin/main)
  if git push origin HEAD:main; then
    echo "commit_sha=$(git rev-parse HEAD)" >> "$GITHUB_OUTPUT"
    echo "commit_created=$(git show -s --format=%cI HEAD)" >> "$GITHUB_OUTPUT"
    echo "push_completed=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$GITHUB_OUTPUT"
    exit 0
  fi
  git fetch origin main
  if [ "$(git rev-parse origin/main)" = "$baseline" ]; then
    echo "Push failed without a main advance; refusing a blind retry" >&2
    exit 1
  fi
  # Validate against the newly published ledger BEFORE replaying our commit.
  python scripts/verify_publication.py --root incoming-publication --baseline-ref origin/main --evidence publication-retry-check.json
  if python -c 'import json,sys; sys.exit(0 if json.load(open("publication-retry-check.json"))["duplicate_close"] else 1)'; then
    echo "A complete close now exists; retaining it without another push"
    echo "duplicate_close=true" >> "$GITHUB_OUTPUT"
    exit 0
  fi
  if [ "$attempt" = 3 ]; then
    echo "Main advanced during all three push attempts; publication stopped" >&2
    exit 1
  fi
  if ! git rebase origin/main; then
    git rebase --abort
    echo "Publication conflicts with current main; refusing to overwrite it" >&2
    exit 1
  fi
  python scripts/validate_publication.py --root incoming-publication
 done
