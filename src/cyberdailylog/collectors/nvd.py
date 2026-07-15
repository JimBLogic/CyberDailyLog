from datetime import datetime, timezone
from .base import BaseCollector
from cyberdailylog.models import IntelligenceItem
class NvdCollector(BaseCollector):
    name='nvd'; required=True; endpoint='https://services.nvd.nist.gov/rest/json/cves/2.0'
    def _parse_dt(self,v): return datetime.fromisoformat(v.replace('Z','+00:00')).astimezone(timezone.utc)
    def _item(self, obj):
        cve=obj['cve']; cid=cve['id']; metrics=cve.get('metrics',{}); cvss=None; ver=None; vec=None; sev=None
        for key in ('cvssMetricV40','cvssMetricV31','cvssMetricV30'):
            if key in metrics:
                m=metrics[key][0]; d=m.get('cvssData',{}); cvss=d.get('baseScore'); ver=d.get('version'); vec=d.get('vectorString'); sev=m.get('baseSeverity') or d.get('baseSeverity'); break
        desc=next((d['value'] for d in cve.get('descriptions',[]) if d.get('lang')=='en'), '')
        refs=[r.get('url','') for r in cve.get('references',{}).get('referenceData',[]) if r.get('url')]
        item=IntelligenceItem(canonical_id=cid,title=f"{cid}: {desc[:120]}",summary=desc,category='vulnerability',source_name='NVD CVE API 2.0',source_type='vulnerability_database',source_tier=1,source_url=f'https://nvd.nist.gov/vuln/detail/{cid}',published_at=self._parse_dt(cve['published']),modified_at=self._parse_dt(cve['lastModified']),cve_ids=[cid],cvss_version=ver,cvss_score=cvss,cvss_vector=vec,severity=sev,references=refs,confidence='medium')
        item.add_provenance('cvss_score','NVD',cvss); return item
    def collect(self,since,until):
        started=datetime.now(timezone.utc)
        try:
            if self.offline: data=self.fixture_json('nvd_page1.json'); pages=[data,self.fixture_json('nvd_page2.json')]
            else:
                headers={'apiKey':self.token} if self.token else {}; params={'pubStartDate':since.strftime('%Y-%m-%dT%H:%M:%S.000'),'pubEndDate':until.strftime('%Y-%m-%dT%H:%M:%S.000'),'resultsPerPage':2000,'startIndex':0}; pages=[]
                while True:
                    data=self.http.get(self.endpoint,headers=headers,params=params,expect_json=True).json(); pages.append(data)
                    if params['startIndex']+data.get('resultsPerPage',0)>=data.get('totalResults',0): break
                    params['startIndex']+=data.get('resultsPerPage',0)
            items=[]; received=0; rejected=0
            for data in pages:
                for obj in data.get('vulnerabilities',[]):
                    received+=1
                    if obj['cve'].get('vulnStatus')=='Rejected': rejected+=1; continue
                    items.append(self._item(obj))
            return items,self.timed_health('fixture_only' if self.offline else 'healthy',started,received,len(items),rejected)
        except Exception as e: return [], self.timed_health('failed',started,err=e)
