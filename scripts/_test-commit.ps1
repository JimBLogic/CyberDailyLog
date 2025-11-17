#!/usr/bin/env powershell
Add-Content -Path README.md -Value "<!-- precommit test $(Get-Date -Format o) -->"
git add README.md
git commit -m 'chore: test pre-commit hook'
