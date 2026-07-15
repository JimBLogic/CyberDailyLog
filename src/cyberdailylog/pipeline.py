import os
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .collectors.cisa_kev import CisaKevCollector
from .collectors.epss import EpssCollector
from .collectors.github_advisories import GitHubAdvisoryCollector
from .collectors.github_releases import GitHubReleaseCollector
from .collectors.nvd import NvdCollector
from .collectors.rss import RssCollector
from .correlation import merge_items
from .http import SafeHttpClient
from .models import Report
from .renderers.json import write_json
from .renderers.markdown import write_markdown
from .scoring import score_items
from .settings import load_yaml
from .source_health import quorum_ok


class Pipeline:
    def __init__(
        self,
        config_dir: Path = Path("config"),
        output_dir: Path = Path("reports"),
        offline: bool = False,
    ) -> None:
        self.config_dir = Path(config_dir)
        self.output_dir = Path(output_dir)
        self.offline = offline
        self.sources = load_yaml(self.config_dir / "sources.yml")
        self.scoring = load_yaml(self.config_dir / "scoring.yml")
        self.technologies = load_yaml(self.config_dir / "technologies.yml")
        allowed_hosts = {
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
        self.http = SafeHttpClient(allowed_hosts)

    def run(
        self,
        since: datetime | None = None,
        until: datetime | None = None,
        lookback_hours: int = 24,
        dry_run: bool = False,
        fail_on_degraded: bool = False,
    ) -> Report:
        until = until or datetime.now(timezone.utc).replace(microsecond=0)
        since = since or until - timedelta(hours=lookback_hours)

        collectors = [
            CisaKevCollector(self.http, offline=self.offline),
            NvdCollector(
                self.http,
                offline=self.offline,
                token=os.getenv("NVD_API_KEY"),
            ),
            GitHubAdvisoryCollector(
                self.http,
                offline=self.offline,
                token=os.getenv("GITHUB_TOKEN"),
            ),
            RssCollector(
                self.http,
                offline=self.offline,
                sources=self.sources.get("rss_sources", []),
            ),
            GitHubReleaseCollector(
                self.http,
                offline=self.offline,
                token=os.getenv("GITHUB_TOKEN"),
                repos=self.sources.get("github_releases", []),
            ),
        ]

        items = []
        health = []
        for collector in collectors:
            collected, collector_health = collector.collect(since, until)
            items.extend(collected)
            health.append(collector_health)

        cves = sorted({cve for item in items for cve in item.cve_ids})
        epss, epss_health = EpssCollector(
            self.http,
            offline=self.offline,
        ).collect_scores(cves)
        health.append(epss_health)

        for item in items:
            for cve in item.cve_ids:
                if cve not in epss:
                    continue
                item.epss_score = epss[cve]["epss_score"]
                item.epss_percentile = epss[cve]["epss_percentile"]
                item.add_provenance("epss_score", "FIRST EPSS", item.epss_score)

        merged = merge_items(items)
        selected = score_items(
            merged,
            self.scoring,
            self.technologies,
            since,
            until,
        )
        report = Report(
            generated_at=datetime.now(timezone.utc).replace(microsecond=0),
            coverage_start=since,
            coverage_end=until,
            degraded=not quorum_ok(health),
            items=selected,
            source_health=health,
        )

        if report.degraded and fail_on_degraded:
            raise SystemExit(2)
        if not dry_run:
            write_markdown(report, self.output_dir)
            write_json(report, self.output_dir)
        return report
