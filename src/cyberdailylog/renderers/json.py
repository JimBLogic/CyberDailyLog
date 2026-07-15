import json
from pathlib import Path
def write_json(report,out:Path):
    out.mkdir(parents=True,exist_ok=True); text=report.model_dump_json(indent=2)
    (out/'latest.json').write_text(text+'\n',encoding='utf-8')
    (out/'source-health.json').write_text(json.dumps([h.to_dict() for h in report.source_health],indent=2,sort_keys=True)+'\n',encoding='utf-8')
    d=report.coverage_end.date(); ad=out/'archive'/f'{d:%Y}'/f'{d:%m}'; ad.mkdir(parents=True,exist_ok=True); (ad/f'{d}.json').write_text(text+'\n',encoding='utf-8')
