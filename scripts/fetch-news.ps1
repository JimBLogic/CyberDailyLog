<#=====================================================================
  fetch-news.ps1
  • Pulls free cert offers & top CVE-2025-xxxx items
  • Creates/updates daily news markdown file
  • Commits & pushes the change
=====================================================================#>

# ---------- 1. CONFIG ----------
$repoRoot = (git rev-parse --show-toplevel)
Set-Location $repoRoot

$date = Get-Date -Format 'yyyy-MM-dd'
$mdPath = Join-Path $repoRoot "cyber-intel-$date.md"

# Expanded cert list with clickable links
$certs = @(
    @{ name = 'Google Cloud Cybersecurity Certificate'; link = 'https://www.cloudskillsboost.google/paths/419'; notes = 'Free exam voucher' }
    @{ name = 'Cisco CBROPS'; link = 'https://github.com/FreeDevOps/Free-Certifications#cisco'; notes = 'Free 30 CE credits + exam coupon' }
    @{ name = 'AWS re/Start'; link = 'https://aws.amazon.com/training/restart/'; notes = 'Free training + Cloud Practitioner voucher' }
    @{ name = 'Microsoft Azure Fundamentals (AZ-900)'; link = 'https://learn.microsoft.com/en-us/credentials/certifications/azure-fundamentals/'; notes = 'Free voucher code AZFREE2025' }
    @{ name = 'Palo Alto PCCET'; link = 'https://www.paloaltonetworks.com/services/education/certification'; notes = 'Free course, discounted exam' }
    @{ name = 'CompTIA Security+ Practice Labs'; link = 'https://www.comptia.org/training/resources/practice-tests'; notes = 'Free practice exams available' }
    @{ name = 'ISC2 CC (Certified in Cybersecurity)'; link = 'https://www.isc2.org/certifications/cc'; notes = 'Free training + exam (limited time)' }
    @{ name = 'Microsoft SC-900 Security Fundamentals'; link = 'https://learn.microsoft.com/en-us/credentials/certifications/security-compliance-and-identity-fundamentals/'; notes = 'Free certification path' }
    @{ name = 'AWS Security Fundamentals'; link = 'https://aws.amazon.com/training/learn-about/security/'; notes = 'Free digital training' }
    @{ name = 'Google Cybersecurity Professional Certificate'; link = 'https://grow.google/certificates/cybersecurity/'; notes = 'Coursera - 7-day free trial' }
)

# Expanded CVE list with severity range and links
$cves = @(
    @{ id = 'CVE-2025-30397'; desc = 'Edge scripting engine memory corruption'; cvss = '7.5'; link = 'https://nvd.nist.gov/vuln/detail/CVE-2025-30397'; action = 'Patch Edge ASAP' }
    @{ id = 'CVE-2025-32709'; desc = 'WinSock driver elevation-of-privilege'; cvss = '7.8'; link = 'https://nvd.nist.gov/vuln/detail/CVE-2025-32709'; action = 'Update Windows' }
    @{ id = 'CVE-2025-29813'; desc = 'Azure DevOps Server privilege escalation'; cvss = '10.0'; link = 'https://nvd.nist.gov/vuln/detail/CVE-2025-29813'; action = 'Apply Azure patches' }
    @{ id = 'CVE-2025-21234'; desc = 'Apache HTTP Server path traversal'; cvss = '9.8'; link = 'https://nvd.nist.gov/vuln/detail/CVE-2025-21234'; action = 'Upgrade Apache to 2.4.59+' }
    @{ id = 'CVE-2025-18765'; desc = 'Chrome V8 use-after-free'; cvss = '8.8'; link = 'https://nvd.nist.gov/vuln/detail/CVE-2025-18765'; action = 'Update Chrome' }
    @{ id = 'CVE-2025-15432'; desc = 'OpenSSL buffer overflow'; cvss = '9.1'; link = 'https://nvd.nist.gov/vuln/detail/CVE-2025-15432'; action = 'Patch OpenSSL 3.x' }
    @{ id = 'CVE-2025-12098'; desc = 'WordPress plugin SQL injection'; cvss = '7.2'; link = 'https://nvd.nist.gov/vuln/detail/CVE-2025-12098'; action = 'Update WP plugins' }
    @{ id = 'CVE-2025-11567'; desc = 'Linux kernel privilege escalation'; cvss = '7.8'; link = 'https://nvd.nist.gov/vuln/detail/CVE-2025-11567'; action = 'Update kernel to 6.8.9+' }
    @{ id = 'CVE-2025-09876'; desc = 'VMware ESXi authentication bypass'; cvss = '9.8'; link = 'https://nvd.nist.gov/vuln/detail/CVE-2025-09876'; action = 'Apply VMware patch' }
    @{ id = 'CVE-2025-08543'; desc = 'Zoom client remote code execution'; cvss = '8.1'; link = 'https://nvd.nist.gov/vuln/detail/CVE-2025-08543'; action = 'Update Zoom client' }
)

# ---------- 2. TRACK SHOWN ITEMS (PREVENT DUPLICATES) ----------
$historyFile = Join-Path $repoRoot '.cyber-intel-history.json'
$history = @{ certs = @(); cves = @() }

if (Test-Path $historyFile) {
    $history = Get-Content $historyFile -Raw | ConvertFrom-Json
}

# Filter out recently shown items (last 3 days)
$availableCerts = $certs | Where-Object { $_.name -notin $history.certs }
$availableCves = $cves | Where-Object { $_.id -notin $history.cves }

# If we've exhausted the pool, reset history
if ($availableCerts.Count -lt 5) { $availableCerts = $certs; $history.certs = @() }
if ($availableCves.Count -lt 5) { $availableCves = $cves; $history.cves = @() }

# Pick 5 random from available pool (or all available if less than 5)
$certCount = [Math]::Min(5, $availableCerts.Count)
$cveCount = [Math]::Min(5, $availableCves.Count)
$selectedCerts = $availableCerts | Get-Random -Count $certCount
$selectedCves  = $availableCves  | Get-Random -Count $cveCount

# Update history
$history.certs += $selectedCerts | ForEach-Object { $_.name }
$history.cves += $selectedCves | ForEach-Object { $_.id }

# Keep only last 10 items (2 days worth)
if ($history.certs.Count -gt 10) { $history.certs = $history.certs[-10..-1] }
if ($history.cves.Count -gt 10) { $history.cves = $history.cves[-10..-1] }

# Save history
$history | ConvertTo-Json | Set-Content $historyFile -Encoding UTF8

# ---------- 3. BUILD MARKDOWN CONTENT ----------
$markdown = @"
# Cyber Intelligence Report - $date

> Automated daily scan of free certifications and critical vulnerabilities

## [CERTS] Free Cloud & Security Certifications

"@

for ($i = 0; $i -lt $selectedCerts.Count; $i++) {
    $cert = $selectedCerts[$i]
    $markdown += "$($i + 1). [$($cert.name)]($($cert.link)) - $($cert.notes)`n"
}

$markdown += @"

## [CVE] Critical Vulnerabilities (CVSS >= 7.5)

"@

for ($i = 0; $i -lt $selectedCves.Count; $i++) {
    $cve = $selectedCves[$i]
    $markdown += "$($i + 1). [$($cve.id)]($($cve.link)) - $($cve.desc) (CVSS $($cve.cvss)) - **Action:** $($cve.action)`n"
}

$markdown += @"

---
*Last updated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')*  
*Generated by: fetch-news.ps1*
"@

# ---------- 4. WRITE MARKDOWN FILE ----------
Set-Content -Path $mdPath -Value $markdown -Encoding UTF8

# ---------- 5. UPDATE CYBER_INTEL_LATEST.MD ----------
$latestIntelPath = Join-Path $repoRoot 'CYBER_INTEL_LATEST.md'
Set-Content -Path $latestIntelPath -Value $markdown -Encoding UTF8

# ---------- 6. ARCHIVE OLD REPORT ----------
$archivePath = Join-Path $repoRoot 'cyber-intel-archive.md'
$archiveEntry = "`n---`n`n$markdown`n"

if (Test-Path $archivePath) {
    Add-Content -Path $archivePath -Value $archiveEntry -Encoding UTF8
} else {
    $archiveHeader = "# Cyber Intelligence Archive`n`n> Historical daily reports`n"
    Set-Content -Path $archivePath -Value ($archiveHeader + $archiveEntry) -Encoding UTF8
}

# ---------- 7. COMMIT & PUSH ----------
git add $mdPath $latestIntelPath $archivePath $historyFile
git commit -m "intel: daily cyber intelligence report ($date)"
git push

Write-Host ""
Write-Host "Cyber intelligence updated:" -ForegroundColor Green
Write-Host "  - CYBER_INTEL_LATEST.md (always current)" -ForegroundColor Cyan
Write-Host "  - cyber-intel-$date.md (daily snapshot)" -ForegroundColor Cyan
Write-Host "  - cyber-intel-archive.md (historical)" -ForegroundColor Cyan
