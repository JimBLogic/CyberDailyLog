#!/usr/bin/env bash
# fetch-news.sh – pulls free certs + top CVEs, appends to daily-log.csv,
# commits & pushes the change.

set -euo pipefail
IFS=$'\n\t'

# ----- CONFIG -----
REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"
CSV_PATH="daily-log.csv"

# Static lists (replace with live API calls if you wish)
CERTS=(
  "Google Cloud Cybersecurity Certificate – free exam voucher (cloudskillsboost.google/paths/419)"
  "Cisco CBROPS – free 30 CE credits + exam coupon (GitHub Free-Certifications)"
  "AWS re/Start – free training + Cloud Practitioner voucher (GitHub Free-Certifications)"
  "Microsoft Azure Fundamentals (AZ-900) – free voucher AZFREE2025 (GitHub Free-Certifications)"
  "Palo Alto PCCET – free course discounted exam (paloaltonetworks.com)"
)

CVES=(
  "CVE-2025-30397 – Edge scripting engine memory corruption (CVSS 7.5) – patch Edge ASAP"
  "CVE-2025-32709 – WinSock driver elevation-of-privilege (CVSS 7.8) – update Windows"
  "CVE-2025-29813 – Azure DevOps Server privilege escalation (CVSS 10.0) – apply Azure patches"
)

# ----- PICK RANDOM 3 FROM EACH -----
SELECTED_CERTS=$(printf "%s\n" "${CERTS[@]}" | shuf -n3 | tr '\n' ';' | sed 's/;$//')
SELECTED_CVES=$(printf "%s\n" "${CVES[@]}" | shuf -n3 | tr '\n' ';' | sed 's/;$//')

# ----- BUILD CSV LINE -----
DATE=$(date +%F)
TASK="Daily cyber-sec news scan"
NOTE="Certs: ${SELECTED_CERTS} | CVEs: ${SELECTED_CVES}"
LINE="${DATE},News,${TASK},${NOTE}"

# Append to CSV
echo "$LINE" >> "$CSV_PATH"

# ----- COMMIT & PUSH -----
git add "$CSV_PATH"
git commit -m "🗞️ Daily cyber-sec news + 1% improvement (${DATE})"
git push

echo -e "\n✅ Added entry for $DATE"
