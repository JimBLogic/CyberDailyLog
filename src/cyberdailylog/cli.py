import argparse, json
from datetime import datetime, timezone
from pathlib import Path
from .pipeline import Pipeline

def dt(s): return datetime.fromisoformat(s.replace('Z','+00:00')).astimezone(timezone.utc)
def main(argv=None):
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='cmd',required=True)
    for name in ['collect','generate','run','validate','source-health']:
        sp=sub.add_parser(name); sp.add_argument('--since'); sp.add_argument('--until'); sp.add_argument('--lookback-hours',type=int,default=24); sp.add_argument('--output-dir',default='reports'); sp.add_argument('--config-dir',default='config'); sp.add_argument('--dry-run',action='store_true'); sp.add_argument('--offline-fixtures',action='store_true'); sp.add_argument('--log-level',default='INFO'); sp.add_argument('--fail-on-degraded',action='store_true')
    a=p.parse_args(argv)
    if a.cmd in {'run','collect','generate','source-health'}:
        r=Pipeline(Path(a.config_dir),Path(a.output_dir),a.offline_fixtures).run(dt(a.since) if a.since else None, dt(a.until) if a.until else None, a.lookback_hours, a.dry_run, a.fail_on_degraded)
        if a.cmd=='source-health': print(json.dumps([h.to_dict() for h in r.source_health],indent=2))
        else: print(f'Generated {len(r.items)} selected items; degraded={r.degraded}')
    elif a.cmd=='validate':
        for f in [Path(a.output_dir)/'latest.json', Path(a.output_dir)/'source-health.json']:
            if f.exists(): json.loads(f.read_text())
        print('Validation OK')
if __name__=='__main__': main()
