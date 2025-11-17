<#=====================================================================
  fetch-news.ps1
  • Pulls free cert offers & top CVE-2025-xxxx items
  • Appends a line to daily-log.csv
  • Commits & pushes the change
=====================================================================#>

# ---------- 1. CONFIG ----------
$repoRoot = (git rev-parse --show-toplevel)
Set-Location $repoRoot

$csvPath = Join-Path $repoRoot 'daily-log.csv'

# Static lists – you can replace these with live API calls later
$certs = @(
    'Google Cloud Cybersecurity Certificate – free exam voucher (cloudskillsboost.google/paths/419)'
    'Cisco CBROPS – free 30 CE credits + exam coupon (GitHub Free-Certifications)'
    'AWS re/Start – free training + Cloud Practitioner voucher (GitHub Free-Certifications)'
    'Microsoft Azure Fundamentals (AZ-900) – free voucher AZFREE2025 (GitHub Free-Certifications)'
    'Palo Alto PCCET – free course discounted exam (paloaltonetworks.com)'
)

$cves = @(
    'CVE-2025-30397 – Edge scripting engine memory corruption (CVSS 7.5) – patch Edge ASAP'
    'CVE-2025-32709 – WinSock driver elevation-of-privilege (CVSS 7.8) – update Windows'
    'CVE-2025-29813 – Azure DevOps Server privilege escalation (CVSS 10.0) – apply Azure patches'
)

# ---------- 2. PICK TOP 3 FROM EACH ----------
$selectedCerts = $certs | Get-Random -Count 3
$selectedCves  = $cves  | Get-Random -Count 3

# Build a concise note (max ~250 chars so the CSV stays readable)
$certList = ($selectedCerts -join '; ')
$cveList = ($selectedCves -join '; ')
$task = "Daily cyber-sec news scan"
$note = "Certs: $certList | CVEs: $cveList"

# ---------- 3. APPEND TO CSV ----------
$date = Get-Date -Format 'yyyy-MM-dd'
$line = "$date,News,$task,$note"
Add-Content -Path $csvPath -Value $line -Encoding UTF8

# ---------- 4. COMMIT & PUSH ----------
git add $csvPath
git commit -m "Daily cyber-sec news + 1% improvement ($date)"
git push

Write-Host ""
Write-Host "Done - added entry for $date" -ForegroundColor Green
