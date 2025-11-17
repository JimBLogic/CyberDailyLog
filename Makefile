.PHONY: help install-hooks install-hooks-windows install-hooks-unix validate-csv

help:
	@echo "Available make targets:"
	@echo "  help                   – Show this help message"
	@echo "  install-hooks          – Detect OS and install Git hooks"
	@echo "  install-hooks-windows  – Force Windows PowerShell installer"
	@echo "  install-hooks-unix     – Force Bash installer"
	@echo "  validate-csv           – Run the CSV validator"

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
