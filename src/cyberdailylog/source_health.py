def quorum_ok(health):
    kev=any(h.source=='cisa_kev' and h.status in {'healthy','fixture_only'} for h in health)
    major=any(h.source in {'nvd','github_advisories'} and h.status in {'healthy','fixture_only'} for h in health)
    return kev and major
