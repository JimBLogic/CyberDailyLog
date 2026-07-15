from pathlib import Path
from datetime import datetime, timezone, timedelta
import os
from .settings import load_yaml
from .http import SafeHttpClient
from .models import Report
from .collectors.cisa_kev import CisaKevCollector
from .collectors.nvd import NvdCollector
from .collectors.epss import EpssCollector
from .collectors.github_advisories import GitHubAdvisoryCollector
from .collectors.rss import RssCollector
from .collectors.github_releases import GitHubReleaseCollector
from .correlation import merge_items
from .scoring import score_items
from .source_health import quorum_ok
from .renderers.markdown import write_markdown
from .renderers.json import write_json
class Pipeline:
    def __init__(self,config_dir=Path('config'),output_dir=Path('reports'),offline=False):
        self.config_dir=Path(config_dir); self.output_dir=Path(output_dir); self.offline=offline
        self.sources=load_yaml(self.config_dir/'sources.yml'); self.scoring=load_yaml(self.config_dir/'scoring.yml'); self.tech=load_yaml(self.config_dir/'technologies.yml')
        hosts={'www.cisa.gov','services.nvd.nist.gov','api.first.org','api.github.com','msrc.microsoft.com','sec.cloudapps.cisco.com','access.redhat.com','ubuntu.com','www.debian.org','chromereleases.googleblog.com'}
        self.http=SafeHttpClient(hosts)
    def run(self,since=None,until=None,lookback_hours=24,dry_run=False,fail_on_degraded=False):
        until=until or datetime.now(timezone.utc).replace(microsecond=0); since=since or until-timedelta(hours=lookback_hours)
        collectors=[CisaKevCollector(self.http,offline=self.offline),NvdCollector(self.http,offline=self.offline,token=os.getenv('NVD_API_KEY')),GitHubAdvisoryCollector(self.http,offline=self.offline,token=os.getenv('GITHUB_TOKEN')),RssCollector(self.http,offline=self.offline,sources=self.sources.get('rss_sources',[])),GitHubReleaseCollector(self.http,offline=self.offline,token=os.getenv('GITHUB_TOKEN'),repos=self.sources.get('github_releases',[]))]
        items=[]; health=[]
        for c in collectors:
            got,h=c.collect(since,until); items+=got; health.append(h)
        cves=sorted({c for i in items for c in i.cve_ids})
        epss,h=EpssCollector(self.http,offline=self.offline).collect_scores(cves); health.append(h)
        for i in items:
            for c in i.cve_ids:
                if c in epss:
                    i.epss_score=epss[c]['epss_score']; i.epss_percentile=epss[c]['epss_percentile']; i.add_provenance('epss_score','FIRST EPSS',i.epss_score)
        merged=merge_items(items); selected=score_items(merged,self.scoring,self.tech,since,until)
        report=Report(generated_at=datetime.now(timezone.utc).replace(microsecond=0),coverage_start=since,coverage_end=until,degraded=not quorum_ok(health),items=selected,source_health=health)
        if report.degraded and fail_on_degraded: raise SystemExit(2)
        if not dry_run:
            write_markdown(report,self.output_dir); write_json(report,self.output_dir)
        return report
