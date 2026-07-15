# Scoring methodology

`config/scoring.yml` defines deterministic weights: CISA KEV +50, confirmed exploitation +40, known ransomware use +25, critical CVSS +20, high CVSS +10, EPSS >= 0.70 +25, EPSS >= 0.30 +15, EPSS percentile >= 0.95 +10, priority technology +8, official source +5, detection opportunity +5, and metadata-only modification -5. These are initial engineering values, not scientific truth.
