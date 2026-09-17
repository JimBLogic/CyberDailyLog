from pathlib import Path
from datetime import datetime, timezone
import os
from urllib.parse import urlparse

from .settings import load_yaml
from .http import SafeHttpClient
from .models import Report
from .collectors.cisa_kev import CisaKevCollector
from .collectors.nvd import NvdCollector
from .collectors.epss import EpssCollector
from .collectors.github_advisories import GitHubAdvisoryCollector
from .collectors.rss import RssCollector
from .collectors.github_releases import GitHubReleaseCollector
from .collectors.hacker_news import HackerNewsCollector
from .state import StateLedger, coverage_start
from .operational_evidence import load_operational_evidence
from .source_health import quorum_ok
from .renderers.markdown import write_markdown
from .renderers.json import write_json


class Pipeline:
    def __init__(self, config_dir=Path("config"), output_dir=Path("reports"), offline=False):
        self.config_dir = Path(config_dir)
        self.output_dir = Path(output_dir)
        self.offline = offline
        self.sources = load_yaml(self.config_dir / "sources.yml")
        self.scoring = load_yaml(self.config_dir / "scoring.yml")
        self.report_config = load_yaml(self.config_dir / "report.yml")
        self.tech = load_yaml(self.config_dir / "technologies.yml")
        hosts = {
            "www.cisa.gov",
            "services.nvd.nist.gov",
            "api.first.org",
            "api.github.com",
            "msrc.microsoft.com",
            "sec.cloudapps.cisco.com",
            "access.redhat.com",
            "ubuntu.com",
            "www.debian.org",
            "chromereleases.googleblog.com",
        }
        for source in self.sources.get("rss_sources", []):
            if source.get("enabled", True):
                host = urlparse(str(source.get("url") or "")).hostname
                if host:
                    hosts.add(host)
        hacker_news = self.sources.get("hacker_news", {})
        if hacker_news.get("enabled", False):
            host = urlparse(str(hacker_news.get("base_url") or "")).hostname
            if host:
                hosts.add(host)
        self.http = SafeHttpClient(hosts)

    def run(self, since=None, until=None, lookback_hours=24, dry_run=False, fail_on_degraded=False):
        until = until or datetime.now(timezone.utc).replace(microsecond=0)
        ledger = StateLedger(self.output_dir / "cti-state.json")
        ledger.seed_archives(self.output_dir)
        since = since or coverage_start(ledger, until, lookback_hours)
        rss_collectors = [
            RssCollector(self.http, offline=self.offline, sources=[source])
            for source in self.sources.get("rss_sources", [])
            if source.get("enabled", True)
        ]
        collectors = [
            CisaKevCollector(self.http, offline=self.offline),
            NvdCollector(self.http, offline=self.offline, token=os.getenv("NVD_API_KEY")),
            GitHubAdvisoryCollector(self.http, offline=self.offline, token=os.getenv("GITHUB_TOKEN")),
            *rss_collectors,
            GitHubReleaseCollector(
                self.http,
                offline=self.offline,
                token=os.getenv("GITHUB_TOKEN"),
                repos=self.sources.get("github_releases", []),
            ),
        ]
        hacker_news = self.sources.get("hacker_news", {})
        if hacker_news.get("enabled", False):
            collectors.append(HackerNewsCollector(self.http, offline=self.offline, config=hacker_news))

        items = load_operational_evidence(self.config_dir / "operational-evidence.yml")
        health = []
        for collector in collectors:
            got, source_health = collector.collect(since, until)
            items += got
            health.append(source_health)
        cves = sorted({cve for item in items for cve in item.cve_ids})
        epss, epss_health = EpssCollector(self.http, offline=self.offline).collect_scores(cves)
        health.append(epss_health)
        for item in items:
            for cve in item.cve_ids:
                if cve in epss:
                    item.epss_score = float(epss[cve]["epss_score"])
                    item.epss_percentile = float(epss[cve]["epss_percentile"])
                    item.add_provenance("epss_score", "FIRST EPSS", item.epss_score)
        if fail_on_degraded and not quorum_ok(health):
            raise SystemExit(2)
        for item in items:
            if any(cve in self.tech.get("confirmed_critical_asset_cves", []) for cve in item.cve_ids):
                item.critical_asset_exposure = True
        selected = ledger.observe(
            items, datetime.now(timezone.utc).replace(microsecond=0), since, until, self.tech, self.scoring
        )
        report = Report(
            generated_at=datetime.now(timezone.utc).replace(microsecond=0),
            coverage_start=since,
            coverage_end=until,
            degraded=not quorum_ok(health),
            items=selected,
            source_health=health,
            cti_summary={
                "new_vulnerabilities": sum(i.discovery_type == "new_vulnerability" for i in selected),
                "state_changes": sum(bool(i.transition_type) for i in selected),
                "kev_transitions": sum("entered_cisa_kev" in i.transition_type for i in selected),
                "ransomware_transitions": sum("ransomware_linked" in i.transition_type for i in selected),
                "tracked_vulnerabilities": len(ledger.records),
            },
        )
        if report.degraded and fail_on_degraded:
            raise SystemExit(2)
        write_markdown(report, self.output_dir, self.report_config)
        write_json(report, self.output_dir)
        if not dry_run and not report.degraded:
            ledger.save()
        return report
