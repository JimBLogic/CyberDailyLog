.PHONY: install-hooks install-hooks-windows install-hooks-unix validate-csv

install-hooks:
	@echo "Detecting environment and installing hooks..."
	@if [ "$(OS)" = "Windows_NT" ]; then \
		powershell -NoProfile -ExecutionPolicy Bypass -File scripts/install-githooks.ps1 ; \
	else \
		./scripts/install-githooks.sh ; \
	fi

install-hooks-windows:
	@powershell -NoProfile -ExecutionPolicy Bypass -File scripts/install-githooks.ps1

install-hooks-unix:
	@./scripts/install-githooks.sh

validate-csv:
	@python3 scripts/validate_csv.py
