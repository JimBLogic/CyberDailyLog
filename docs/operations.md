# Operations

First real run:

1. Enable GitHub Actions for the repository.
2. Optionally add `NVD_API_KEY` and use the default `GITHUB_TOKEN` supplied by Actions.
3. Run the `Daily Blue Team Intelligence` workflow manually with `dry_run=true`.
4. Review uploaded reports and source health.
5. Run it again with `dry_run=false` to publish report files if quorum succeeds.

Core quorum requires CISA KEV and at least one of NVD or GitHub Advisories. EPSS/RSS/release failure degrades but does not by itself block publication.
