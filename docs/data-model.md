# Data model

The canonical model is `IntelligenceItem` in `src/cyberdailylog/models.py`. It includes identifiers, source metadata, source tiers, official-source flag, published/modified/collected UTC timestamps, CVE/GHSA IDs, vendor/product/version fields, CVSS, EPSS, KEV fields, exploitation and ransomware flags, references, recommended actions, detection opportunities, Blue Team relevance, confidence, deterministic selection score, selection reasons, and field-level provenance.

Per-CVE state adds `first_seen`, `last_seen`, `state_changed_at`, `discovery_type`, `transition_type`, `previous_state`, `current_state`, `state_transitions`, `priority_before`, `priority_after`, `priority_level` and `priority_level_before`. Evidence fields include nullable `vendor_confirmed_exploitation`, `public_exploit`, `critical_asset_exposure`, plus `cisa_due_date` and `cisa_required_action`. Nullable flags mean unknown rather than confirmed absence.

`discovery_type` distinguishes `new_vulnerability` from `state_transition`. Events retain a stable ID, observed timestamp, changed fields, previous/current values, source URLs and priority before/after. `reports/cti-state.json` schema 2 persists source observations independently of the daily report. `cti_summary` records daily discoveries, changes, KEV/ransomware transitions and total tracked CVEs. Historical reports without those measurements display unavailable values rather than invented zeroes.

The first observation is the earliest retained observation, not the vulnerability disclosure date. See [migration and transition semantics](cti-reliability.md).
