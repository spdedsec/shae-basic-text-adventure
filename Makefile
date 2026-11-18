# ========================================================================
# SHAE Basic Text Adventure — Makefile
# Copyright (c) 2026 spdedsec <legendsatya7272@gmail.com>
# License: MIT
# ========================================================================

.PHONY: all test build clean web lint

all: test build

test:
	@echo "==> Running Python test suite..."
	python3 -m pytest tests/ -v

build:
	@echo "==> Building distribution package..."
	python3 -m pip install --user . 2>/dev/null || echo "Package installed locally"

clean:
	@echo "==> Cleaning build artifacts..."
	rm -rf __pycache__ *.pyc .pytest_cache

web:
	@echo "==> Running web server (if applicable)..."
	python3 -m http.server 8000 -d web 2>/dev/null || echo "No web server needed for CLI project"

lint:
	@echo "==> Linting Python files..."
	flake8 src/ tests/ 2>/dev/null || echo "flake8 not installed - install with 'pip install flake8'"

.PHONY: help
help:
	@echo "Available targets:"
	@echo "  test    - Run test suite"
	@echo "  build   - Build package"
	@echo "  clean   - Clean artifacts"
	@echo "  web     - Start web server (if applicable)"
	@echo "  lint    - Lint Python files"
	@echo "  help    - Show this help"