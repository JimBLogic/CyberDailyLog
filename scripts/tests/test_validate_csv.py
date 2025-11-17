import tempfile
from pathlib import Path
from scripts.validate_csv import validate_and_normalize


def write_and_validate(tmp_path, content: str):
    p = tmp_path / 'daily-log.csv'
    p.write_text(content, encoding='utf-8')
    return validate_and_normalize(p)


def test_empty_file_creates_header(tmp_path):
    code, messages, modified = write_and_validate(tmp_path, '')
    assert code == 0
    assert modified
    assert any('header' in m.lower() for m in messages)
    assert (tmp_path / 'daily-log.csv').read_text().startswith('date,pillar,task,notes')


def test_date_normalization(tmp_path):
    # US-style date should be normalized to YYYY-MM-DD
    content = '11/17/2025,eng,work,notes\n'
    code, messages, modified = write_and_validate(tmp_path, content)
    assert code == 0
    assert modified
    out = (tmp_path / 'daily-log.csv').read_text()
    assert '2025-11-17' in out


def test_invalid_row_detected(tmp_path):
    content = 'date,pillar,task,notes\n2025-11-17,only-two-columns\n'
    code, messages, modified = write_and_validate(tmp_path, content)
    assert code == 2
    assert any('Invalid CSV line' in m for m in messages)
