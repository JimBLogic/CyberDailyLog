from datetime import datetime, timezone
from .base import BaseCollector
from cyberdailylog.models import IntelligenceItem
class CisaKevCollector(BaseCollector):
    name='cisa_kev'; required=True; url='https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json'
    def collect(self,since,until):
        started=datetime.now(timezone.utc)
        try:
            data=self.fixture_json('cisa_kev.json') if self.offline else self.http.get(self.url,expect_json=True).json()
            items=[]
            for v in data.get('vulnerabilities',[]):
                date=datetime.fromisoformat(v.get('dateAdded','1970-01-01')).replace(tzinfo=timezone.utc)
                if not (since <= date <= until): continue
                cve=v['cveID']; title=f"{cve} exploited in CISA KEV: {v.get('vendorProject','')} {v.get('product','')}".strip()
                item=IntelligenceItem(canonical_id=cve,title=title,summary=v.get('shortDescription',''),category='vulnerability',source_name='CISA Known Exploited Vulnerabilities',source_type='government_kev',source_tier=1,source_url=self.url,published_at=date,modified_at=date,cve_ids=[cve],vendors=[v.get('vendorProject','')],products=[v.get('product','')],cisa_kev=True,kev_date_added=date,known_exploited=True,known_ransomware_use=(v.get('knownRansomwareCampaignUse')=='Known'),exploitation_status='confirmed_exploitation',recommended_actions=[v.get('requiredAction','')],references=[v.get('notes','') or self.url],confidence='high')
                item.add_provenance('known_exploited', 'CISA KEV', True); items.append(item)
            return items,self.timed_health('fixture_only' if self.offline else 'healthy',started,len(data.get('vulnerabilities',[])),len(items))
        except Exception as e: return [], self.timed_health('failed',started,err=e)
