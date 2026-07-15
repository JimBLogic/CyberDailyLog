from datetime import datetime, timezone
from .base import BaseCollector
from cyberdailylog.models import IntelligenceItem
class GitHubReleaseCollector(BaseCollector):
    name='github_releases'; required=False
    def __init__(self,*a,repos=None,**kw): super().__init__(*a,**kw); self.repos=repos or []
    def _dt(self,v): return datetime.fromisoformat(v.replace('Z','+00:00')).astimezone(timezone.utc)
    def collect(self,since,until):
        started=datetime.now(timezone.utc); items=[]; rec=0
        try:
            data=self.fixture_json('github_releases.json') if self.offline else {r:self.http.get(f'https://api.github.com/repos/{r}/releases',headers={'Authorization':f'Bearer {self.token}'} if self.token else {},expect_json=True).json() for r in self.repos}
            for repo, rels in data.items():
                for rel in rels:
                    rec+=1; dt=self._dt(rel['published_at'])
                    if since <= dt <= until:
                        items.append(IntelligenceItem(canonical_id=f"release:{repo}:{rel['tag_name']}",title=f"{repo} {rel['tag_name']}",summary=rel.get('name') or '',category='tool_release',source_name='GitHub Releases',source_type='defensive_tool_release',source_tier=3,source_url=rel['html_url'],published_at=dt,modified_at=dt,references=[rel['html_url']],blue_team_relevance='Allowlisted defensive project release; review release notes for detection or monitoring updates.',detection_opportunities=['Review release notes for defensive content changes.'],confidence='medium'))
            return items,self.timed_health('fixture_only' if self.offline else 'healthy',started,rec,len(items))
        except Exception as e: return items,self.timed_health('degraded',started,rec,len(items),err=e)
