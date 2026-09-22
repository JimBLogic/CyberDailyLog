from datetime import datetime
from pathlib import Path
import runpy
import sys
import json
from types import SimpleNamespace

adapter = runpy.run_path(str(Path("scripts/dispatch_due.py")))
decision = adapter["decision"]


def at(stamp):
    return datetime.fromisoformat(stamp.replace("Z", "+00:00"))


def test_external_timer_uses_madrid_noon_and_dst():
    for stamp, target in [
        ("2026-09-22T10:00:00Z", "2026-09-22T10:00:00+00:00"),
        ("2026-12-22T11:20:00Z", "2026-12-22T11:00:00+00:00"),
        ("2026-03-29T10:40:00Z", "2026-03-29T10:00:00+00:00"),
    ]:
        plan = decision(at(stamp), {})
        assert plan["dispatch"] is True and plan["scheduled_for"] == target
        assert plan["payload"]["ref"] == "main"
        assert plan["payload"]["inputs"]["trigger_origin"] == "external"
        assert plan["payload"]["inputs"]["dry_run"] is False
    for stamp in ("2026-09-22T09:59:00Z", "2026-09-22T10:12:00Z", "2026-09-22T11:00:00Z"):
        assert decision(at(stamp), {})["dispatch"] is False


def test_external_dispatch_skips_published_day_but_not_missing_or_bad_evidence():
    now = at("2026-09-22T10:20:00Z")
    current = {"schema_version": 2, "status": "on_time", "actual_publication_time": "2026-09-22T10:01:00Z"}
    assert decision(now, current)["dispatch"] is False
    for value in ("2026-09-21T10:01:00Z", "2026-09-22T09:59:00Z", "2099-01-01T12:00:00Z", "invalid"):
        assert decision(now, {**current, "actual_publication_time": value})["dispatch"] is True
    assert decision(now, {**current, "status": "failed"})["dispatch"] is True


def test_cli_previews_without_post_and_apply_sends_only_scoped_dispatch(monkeypatch, capsys):
    state = adapter["main"].__globals__
    monkeypatch.setitem(
        state,
        "datetime",
        SimpleNamespace(now=lambda tz: at("2026-09-22T10:00:00Z"), fromisoformat=datetime.fromisoformat),
    )
    monkeypatch.setitem(state, "load_timing", lambda: {})
    requests = []

    class Accepted:
        status = 204

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    def send(request, timeout):
        requests.append(request)
        return Accepted()

    monkeypatch.setitem(state, "urlopen", send)
    monkeypatch.setattr(sys, "argv", ["dispatch_due.py"])
    assert adapter["main"]() == 0 and not requests
    monkeypatch.setattr(sys, "argv", ["dispatch_due.py", "--apply"])
    monkeypatch.setenv("GH_ACTIONS_TOKEN", "test-credential-never-log")
    assert adapter["main"]() == 0 and len(requests) == 1
    request = requests[0]
    assert request.full_url == adapter["DISPATCH_URL"]
    assert request.method == "POST"
    assert json.loads(request.data)["inputs"]["dispatch_requested_at"] == "2026-09-22T10:00:00+00:00"
    assert "test-credential-never-log" not in capsys.readouterr().out
