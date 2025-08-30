# BNB Trading System - Development Commands

.PHONY: help install install-dev format lint test test-unit test-integration test-slow clean docs pre-commit

# Default target
help:
	@echo "BNB Trading System - Available Commands:"
	@echo ""
	@echo "Setup:"
	@echo "  install      Install production dependencies"
	@echo "  install-dev  Install development dependencies"
	@echo "  pre-commit   Install pre-commit hooks"
	@echo ""
	@echo "Development:"
	@echo "  format       Format code with black and isort"
	@echo "  lint         Run linting with flake8 and mypy"
	@echo "  test         Run all tests"
	@echo "  test-unit    Run unit tests only"
	@echo "  test-integration  Run integration tests"
	@echo "  test-slow    Run slow tests with market data"
	@echo ""
	@echo "Analysis:"
	@echo "  analyze      Run main trading analysis"
	@echo "  backtest     Run 18-month backtest validation"
	@echo "  signal       Generate current trading signal"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean        Clean temporary files and caches"
	@echo "  docs         Generate documentation"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pip install -e .

pre-commit:
	pre-commit install
	pre-commit install --hook-type pre-push

# Code quality
format:
	black src/ tests/ --line-length=100
	isort src/ tests/ --profile=black --line-length=100

lint:
	flake8 src/ tests/ --max-line-length=100 --extend-ignore=E203,W503
	mypy src/ --ignore-missing-imports

# Testing
test:
	pytest tests/ -v --cov=src/bnb_trading --cov-report=html --cov-report=term-missing

test-unit:
	pytest tests/ -v -m "unit" --cov=src/bnb_trading

test-integration:
	pytest tests/ -v -m "integration" --cov=src/bnb_trading

test-slow:
	pytest tests/ -v -m "slow" --tb=short

# Trading analysis
analyze:
	python main.py

backtest:
	python backtester.py

signal:
	python signal_generator.py

# Maintenance
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -name ".coverage" -delete
	find . -name "htmlcov" -type d -exec rm -rf {} +
	find . -name ".pytest_cache" -type d -exec rm -rf {} +
	find . -name ".mypy_cache" -type d -exec rm -rf {} +

docs:
	@echo "Documentation generation with Sphinx (future implementation)"
	@echo "Current docs: README.md, CLAUDE.md, MODULES.md, TODO.md"

# Development workflow
dev-setup: install-dev pre-commit
	@echo "✅ Development environment ready!"
	@echo "Run 'make test' to verify installation"

# CI/CD commands
ci-test: format lint test
	@echo "✅ All CI checks passed!"

# Release preparation
pre-release: clean format lint test
	@echo "✅ Ready for release!"
