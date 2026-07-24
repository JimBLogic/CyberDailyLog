# CyberDailyLog dashboard

This is the portable full-stack presentation layer for the repository's daily intelligence pipeline.

```bash
npm ci
npm run dev
```

The server reads public, generated artifacts from the parent project and exposes normalized API/export routes. No API key is required. The UI includes ranked vulnerability triage, source health, historical charts, multiple analyst/community signals, bilingual controls and an interview-ready explanation of the automated workflow.

See [`../docs/DASHBOARD.md`](../docs/DASHBOARD.md) for architecture, trust boundaries, backend routes and deployment notes.
