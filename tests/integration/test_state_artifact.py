import gzip
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from cyberdailylog.state import write_state

workflow = yaml.safe_load(Path(".github/workflows/daily-intelligence.yml").read_text())
staging = next(
    step["run"]
    for step in workflow["jobs"]["collect"]["steps"]
    if step.get("name") == "Stage bounded publication artifact"
)


@pytest.mark.parametrize("compressed", [True, False])
def test_actual_artifact_script_keeps_baseline_unchanged_and_stages_only_gzip(tmp_path, compressed):
    reports = tmp_path / "reports"
    reports.mkdir()
    (tmp_path / "README.md").write_text("README")
    (reports / "latest.json").write_text('{"coverage_end":"2026-10-18T10:38:59Z"}')
    state = {"schema_version": 2, "vulnerabilities": {}, "catalog_baselined": True, "coverage_end": "retained"}
    baseline = reports / ("cti-state.json.gz" if compressed else "cti-state.json")
    if compressed:
        write_state(baseline, state)
    else:
        baseline.write_text(json.dumps(state))
    previous = baseline.read_bytes()
    env = {**os.environ, "PATH": str(Path(sys.executable).parent) + os.pathsep + os.environ["PATH"]}
    subprocess.run(["bash", "-e", "-c", staging], cwd=tmp_path, env=env, check=True)
    artifact = tmp_path / "publication-output" / "reports"
    assert baseline.read_bytes() == previous
    assert json.loads(gzip.decompress((artifact / "cti-state.json.gz").read_bytes())) == state
    assert not (artifact / "cti-state.json").exists()
    assert (artifact / "latest.json").read_bytes() == (reports / "latest.json").read_bytes()
