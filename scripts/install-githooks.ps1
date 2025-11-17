#!/usr/bin/env powershell
<#
Install and enable repository hooks from `.githooks`.

This script configures the local repo to use the versioned hooks directory
and (on platforms that support it) marks the pre-commit hook executable.
#>

Write-Output "Ensuring .githooks directory exists..."
if (-not (Test-Path -Path '.githooks')) {
    New-Item -ItemType Directory -Path '.githooks' | Out-Null
}

Write-Output "Configuring git to use .githooks as hooks path (local config)..."
git config core.hooksPath .githooks

# If running on a system with chmod (WSL / Git Bash / Unix), try to set +x
if (Get-Command -Name chmod -ErrorAction SilentlyContinue) {
    try {
        chmod +x .githooks/pre-commit
    } catch {
        Write-Output "chmod failed or not supported here; continuing"
    }
}

Write-Output "Done. Git will now use .githooks for hooks (local config)."
