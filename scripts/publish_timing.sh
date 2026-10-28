#!/usr/bin/env bash
# Regenerate this run's evidence against the newest history after a push race.
set -euo pipefail
if [ "${TIMING_CAN_PUBLISH:-true}" != true ]; then
  # Preserve diagnostic output after earlier job-step failure, without publishing it.
  PYTHONPATH=src python3 scripts/publication_timing.py "$@"
  exit 0
fi
if ! git diff --quiet || ! git diff --cached --quiet; then
  echo "Timing publication requires a clean tracked worktree" >&2
  exit 1
fi
git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
for attempt in 1 2 3; do
  baseline=$(git rev-parse origin/main)
  PYTHONPATH=src python3 scripts/publication_timing.py "$@"
  git add reports/publication-timing.json reports/publication-timing-history.json
  if git diff --cached --quiet; then
    exit 0
  fi
  git commit -m "ops: persist publication SLO evidence [skip ci]"
  if git push origin HEAD:main; then
    exit 0
  fi
  if [ "$attempt" = 3 ]; then
    echo "Timing publication exhausted its push budget" >&2
    exit 1
  fi
  git fetch origin main
  updated=$(git rev-parse origin/main)
  if [ "$baseline" = "$updated" ]; then
    echo "Timing push failed without an advancing remote; refusing blind retry" >&2
    exit 1
  fi
  git merge-base --is-ancestor "$baseline" "$updated"
  # Keep the old commit reachable on its branch; never reset or force push.
  # Inputs and milestone environment remain unchanged; only history is refreshed.
  git switch --detach "$updated"
done
