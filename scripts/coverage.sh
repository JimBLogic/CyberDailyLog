#!/usr/bin/env bash
set -euo pipefail

python -m pytest --cov=scripts --cov-report=term --cov-report=xml
coverage html -d coverage_html
