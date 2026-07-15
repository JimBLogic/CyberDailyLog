from datetime import datetime, timezone
from .base import BaseCollector
from cyberdailylog.models import IntelligenceItem
class GitHubAdvisoryCollector(BaseCollector):
    name='github_advisories'; required=True; endpoint='https://api.github.com/advisories'
    def _dt(self,v): return datetime.fromisoformat(v.replace('Z','+00:00')).astimezone(timezone.utc) if v else None
    def _item(self,a):
        ids=[i for i in [a.get('cve_id')] if i]; gh=[a.get('ghsa_id')] if a.get('ghsa_id') else []
        vulns=a.get('vulnerabilities') or []
        item=IntelligenceItem(canonical_id=ids[0] if ids else gh[0],title=a.get('summary',''),summary=a.get('description',''),category='vulnerability',source_name='GitHub Global Security Advisories',source_type='reviewed_advisory',source_tier=1,source_url=a.get('html_url') or a.get('url'),published_at=self._dt(a.get('published_at')),modified_at=self._dt(a.get('updated_at')),cve_ids=ids,ghsa_ids=gh,ecosystems=[v.get('package',{}).get('ecosystem','') for v in vulns if v.get('package')],products=[v.get('package',{}).get('name','') for v in vulns if v.get('package')],affected_versions=[v.get('vulnerable_version_range','') for v in vulns],fixed_versions=[v.get('patched_versions','') for v in vulns if v.get('patched_versions')],severity=a.get('severity'),cvss_score=(a.get('cvss') or {}).get('score'),cvss_vector=(a.get('cvss') or {}).get('vector_string'),references=[r for r in a.get('references',[])],withdrawn=bool(a.get('withdrawn_at')),confidence='high')
        item.add_provenance('fixed_versions','GitHub reviewed advisory',item.fixed_versions); return item
    def collect(self,since,until):
        started=datetime.now(timezone.utc)
        try:
            pages=[self.fixture_json('github_advisories_page1.json'), self.fixture_json('github_advisories_page2.json')] if self.offline else [self.http.get(self.endpoint,headers={'Authorization':f'Bearer {self.token}'} if self.token else {},params={'type':'reviewed','per_page':100},expect_json=True).json()]
            items=[]; rec=0; rej=0
            for data in pages:
                for a in data: rec+=1; item=self._item(a); (items.append(item) if not item.withdrawn else (items.append(item), None))
            return items,self.timed_health('fixture_only' if self.offline else 'healthy',started,rec,len(items),rej)
        except Exception as e: return [], self.timed_health('failed',started,err=e)
