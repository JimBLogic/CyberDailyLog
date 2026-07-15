from .models import SourceHealth


def quorum_ok(health: list[SourceHealth]) -> bool:
    kev_available = any(
        item.source == "cisa_kev" and item.status in {"healthy", "fixture_only"}
        for item in health
    )
    major_available = any(
        item.source in {"nvd", "github_advisories"}
        and item.status in {"healthy", "fixture_only"}
        for item in health
    )
    return kev_available and major_available
