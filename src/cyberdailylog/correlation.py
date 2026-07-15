from urllib.parse import urlsplit, urlunsplit
import hashlib
from .models import IntelligenceItem

def norm_url(u:str)->str:
    p=urlsplit(u); return urlunsplit((p.scheme,p.netloc,p.path.rstrip('/'),'',''))
def key(item:IntelligenceItem)->str:
    if item.cve_ids: return 'cve:'+sorted(item.cve_ids)[0]
    if item.ghsa_ids: return 'ghsa:'+sorted(item.ghsa_ids)[0]
    if item.source_url: return 'url:'+norm_url(item.source_url)
    return 'fp:'+hashlib.sha256((item.title+item.source_name).encode()).hexdigest()[:16]
def merge_items(items:list[IntelligenceItem])->list[IntelligenceItem]:
    out={}
    for item in items:
        k=key(item)
        if k not in out: out[k]=item; continue
        cur=out[k]
        for f in ['cve_ids','ghsa_ids','vendors','products','affected_versions','fixed_versions','weaknesses','ecosystems','references','recommended_actions','detection_opportunities','selection_reasons']:
            setattr(cur,f,sorted({x for x in getattr(cur,f)+getattr(item,f) if x}))
        for f in ['cisa_kev','known_exploited','known_ransomware_use']:
            if getattr(item,f) is True: setattr(cur,f,True); cur.add_provenance(f,item.source_name,True)
        for f in ['epss_score','epss_percentile','kev_date_added','cvss_score','cvss_version','cvss_vector','severity']:
            v=getattr(item,f)
            if getattr(cur,f) is None and v is not None: setattr(cur,f,v); cur.add_provenance(f,item.source_name,v)
            elif v is not None and v != getattr(cur,f): cur.add_provenance(f,item.source_name,v)
        cur.provenance.update({**cur.provenance, **item.provenance})
    return sorted(out.values(), key=lambda i: i.canonical_id)
