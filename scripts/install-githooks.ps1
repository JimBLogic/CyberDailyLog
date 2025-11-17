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

# Prefer PowerShell 7 (pwsh) if available, otherwise fall back to Windows PowerShell
Write-Output "Selecting appropriate hook variant (prefer pwsh)..."
if (Get-Command -Name pwsh -ErrorAction SilentlyContinue) {
    Copy-Item -Path .githooks/pre-commit.pwsh -Destination .githooks/pre-commit -Force
    Write-Output "Using pwsh pre-commit hook"
} else {
    Copy-Item -Path .githooks/pre-commit.powershell -Destination .githooks/pre-commit -Force
    Write-Output "Using Windows PowerShell pre-commit hook"
}

Write-Output "Configuring git to use .githooks as hooks path (local config)..."
git config core.hooksPath .githooks

Write-Output "Marking .githooks/pre-commit as executable in Git index..."
git update-index --add --chmod=+x .githooks/pre-commit

# If running on a system with chmod (WSL / Git Bash / Unix), try to set +x
if (Get-Command -Name chmod -ErrorAction SilentlyContinue) {
    try {
        chmod +x .githooks/pre-commit
    } catch {
        Write-Output "chmod failed or not supported here; continuing"
    }
}

Write-Output "Done. Git will now use .githooks for hooks (local config)."
