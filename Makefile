.PHONY: test lint typecheck validate offline-report
lint:
	ruff check .
	ruff format --check .
typecheck:
	mypy src
test:
	pytest
offline-report:
	python -m cyberdailylog run --offline-fixtures --output-dir tmp/reports
validate:
	python -m cyberdailylog validate --output-dir tmp/reports
