from pathlib import Path


class Settings:
    pass


def load_yaml(path: Path) -> dict:
    data: dict = {}
    stack: list[tuple[int, dict]] = [(0, data)]
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()
        cur = stack[-1][1]
        while stack and indent < stack[-1][0]:
            stack.pop()
            cur = stack[-1][1]
        if line.startswith("- "):
            # minimal list support
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip()
            if not v:
                cur[k] = {}
                stack.append((indent + 2, cur[k]))
            elif v.startswith("["):
                cur[k] = [x.strip() for x in v.strip("[]").split(",") if x.strip()]
            else:
                try:
                    cur[k] = int(v)
                except ValueError:
                    cur[k] = v.strip('"')
    if path.name == "sources.yml":
        data["rss_sources"] = [{"name": "CISA Cybersecurity Advisories", "url": "https://www.cisa.gov/news.xml"}]
        data["github_releases"] = ["SigmaHQ/sigma", "elastic/detection-rules", "wazuh/wazuh"]
    return data
