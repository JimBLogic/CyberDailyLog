#!/usr/bin/env bash
# Install githooks for Unix-like environments (WSL, Git Bash, Linux)
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p .githooks

if command -v pwsh >/dev/null 2>&1; then
  cp .githooks/pre-commit.pwsh .githooks/pre-commit
  echo "Using pwsh pre-commit hook"
elif command -v powershell >/dev/null 2>&1; then
  cp .githooks/pre-commit.powershell .githooks/pre-commit
  echo "Using Windows PowerShell pre-commit hook (powershell)"
else
  # Fallback to pwsh variant if nothing found (it may still work under pwsh path)
  cp .githooks/pre-commit.pwsh .githooks/pre-commit || true
  echo "No pwsh/powershell found; copied pwsh variant to .githooks/pre-commit"
fi

chmod +x .githooks/pre-commit || true
git config core.hooksPath .githooks
echo "Configured git to use .githooks for hooks"
