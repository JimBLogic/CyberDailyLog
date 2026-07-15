from pathlib import Path

def test_workflows_do_not_require_gh_pat_or_csv():
    text='\n'.join(p.read_text(errors='ignore') for p in Path('.github/workflows').glob('*.yml'))
    assert 'custom GitHub personal access token' not in text
    assert 'daily-log.csv' not in text

def test_readme_links_report_not_manual_summary():
    text=Path('README.md').read_text(encoding='utf-8')
    assert 'reports/latest.md' in text
    assert 'Free Cloud' not in text
