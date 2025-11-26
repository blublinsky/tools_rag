.PHONY: help install test test-verbose test-coverage run clean lint format

# Default target
help:
	@echo "Tools-RAG Makefile"
	@echo "=================="
	@echo ""
	@echo "Available targets:"
	@echo "  make install        - Install dependencies in virtual environment"
	@echo "  make test           - Run all tests"
	@echo "  make test-verbose   - Run tests with verbose output"
	@echo "  make test-coverage  - Run tests with coverage report"
	@echo "  make run            - Run the main evaluation script"
	@echo "  make clean          - Clean up cache files and build artifacts"
	@echo "  make lint           - Run linter (pylint)"
	@echo "  make format         - Format code with black"
	@echo ""

# Install dependencies with uv
install:
	@echo "Installing dependencies with uv..."
	@command -v uv >/dev/null 2>&1 || { echo "uv not installed. Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
	uv sync --all-extras
	@echo "✓ Dependencies installed"

# Run tests
test:
	@echo "Running tests..."
	pytest tools_rag/tests/ -v
	@echo "✓ Tests completed"

# Run tests with verbose output
test-verbose:
	@echo "Running tests with verbose output..."
	pytest tools_rag/tests/ -vv -s
	@echo "✓ Tests completed"

# Run tests with coverage
test-coverage:
	@echo "Running tests with coverage..."
	pytest tools_rag/tests/ --cov=tools_rag/src --cov-report=term-missing --cov-report=html
	@echo "✓ Coverage report generated"
	@echo "HTML report: htmlcov/index.html"

# Run main evaluation script
run:
	@echo "Running Tools RAG evaluation..."
	python main.py

# Clean up cache and build files
clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✓ Cleanup completed"

# Run linter (optional - requires pylint)
lint:
	@echo "Running linter..."
	@command -v pylint >/dev/null 2>&1 || { echo "pylint not installed. Install with: pip install pylint"; exit 1; }
	pylint tools_rag
	@echo "✓ Linting completed"

# Format code (optional - requires black)
format:
	@echo "Formatting code..."
	@command -v black >/dev/null 2>&1 || { echo "black not installed. Install with: pip install black"; exit 1; }
	black tools_rag
	@echo "✓ Formatting completed"

