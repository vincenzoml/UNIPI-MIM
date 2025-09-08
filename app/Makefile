# Makefile for Markdown Slides Generator development

.PHONY: help install install-dev test test-cov lint format type-check clean build docs

# Default target
help:
	@echo "Available targets:"
	@echo "  install      - Install package in development mode"
	@echo "  install-dev  - Install with development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linting (flake8)"
	@echo "  format       - Format code (black, isort)"
	@echo "  type-check   - Run type checking (mypy)"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build package"
	@echo "  docs         - Build documentation"
	@echo "  check-deps   - Check external dependencies"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev,docs,rich]"

# Testing
test:
	pytest

test-cov:
	pytest --cov=markdown_slides_generator --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 src/ tests/

format:
	black src/ tests/
	isort src/ tests/

type-check:
	mypy src/

# Build and distribution
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

# Documentation
docs:
	cd docs && make html

# Dependency checking
check-deps:
	@echo "Checking external dependencies..."
	@command -v quarto >/dev/null 2>&1 || echo "❌ Quarto not found - install from https://quarto.org/"
	@command -v quarto >/dev/null 2>&1 && echo "✅ Quarto found: $$(quarto --version)"
	@command -v pdflatex >/dev/null 2>&1 || echo "❌ LaTeX not found - install TeX Live or MiKTeX"
	@command -v pdflatex >/dev/null 2>&1 && echo "✅ LaTeX found: $$(pdflatex --version | head -1)"
	@python -c "import click; print('✅ Click:', click.__version__)" 2>/dev/null || echo "❌ Click not installed"
	@python -c "import yaml; print('✅ PyYAML:', yaml.__version__)" 2>/dev/null || echo "❌ PyYAML not installed"

# Development workflow
dev-setup: install-dev check-deps
	@echo "Development environment setup complete!"

# Run all quality checks
qa: format lint type-check test
	@echo "All quality checks passed!"