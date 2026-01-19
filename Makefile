.PHONY: help install test test-verbose test-coverage run run-rag run-skills run-skills-gpt4o run-compare run-compare-gpt4o clean lint format

# Default target
help:
	@echo "Tools-RAG Makefile"
	@echo "=================="
	@echo ""
	@echo "Available targets:"
	@echo "  make install            - Install dependencies in virtual environment"
	@echo "  make test               - Run all tests"
	@echo "  make test-verbose       - Run tests with verbose output"
	@echo "  make test-coverage      - Run tests with coverage report"
	@echo "  make run                - Run comparison (RAG vs Skills with gpt-4o)"
	@echo "  make run-rag            - Run Hybrid RAG evaluation only"
	@echo "  make run-skills         - Run LLM Skills (gpt-4o-mini)"
	@echo "  make run-skills-gpt4o   - Run LLM Skills (gpt-4o)"
	@echo "  make run-compare        - Run comparison with gpt-4o-mini"
	@echo "  make run-compare-gpt4o  - Run comparison with gpt-4o"
	@echo "  make clean              - Clean up cache files and build artifacts"
	@echo "  make lint               - Run linter (pylint)"
	@echo "  make format             - Format code with black"
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
	uv run pytest tools_rag/tests/ -v
	@echo "✓ Tests completed"

# Run tests with verbose output
test-verbose:
	@echo "Running tests with verbose output..."
	uv run pytest tools_rag/tests/ -vv -s
	@echo "✓ Tests completed"

# Run tests with coverage
test-coverage:
	@echo "Running tests with coverage..."
	uv run pytest tools_rag/tests/ --cov=tools_rag/src --cov-report=term-missing --cov-report=html
	@echo "✓ Coverage report generated"
	@echo "HTML report: htmlcov/index.html"

# Run comparison with gpt-4o (default)
run:
	@echo "Running comparison (RAG vs Skills with gpt-4o)..."
	uv run python main.py --mode compare --model gpt-4o

# Run Hybrid RAG only
run-rag:
	@echo "Running Hybrid RAG evaluation..."
	uv run python main.py --mode rag

# Run LLM Skills with gpt-4o-mini
run-skills:
	@echo "Running LLM Skills evaluation (gpt-4o-mini)..."
	uv run python main.py --mode skills --model gpt-4o-mini

# Run LLM Skills with gpt-4o
run-skills-gpt4o:
	@echo "Running LLM Skills evaluation (gpt-4o)..."
	uv run python main.py --mode skills --model gpt-4o

# Run comparison with gpt-4o-mini
run-compare:
	@echo "Running comparison (gpt-4o-mini)..."
	uv run python main.py --mode compare --model gpt-4o-mini

# Run comparison with gpt-4o
run-compare-gpt4o:
	@echo "Running comparison (gpt-4o)..."
	uv run python main.py --mode compare --model gpt-4o

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
	uv run pylint tools_rag
	@echo "✓ Linting completed"

# Format code (optional - requires black)
format:
	@echo "Formatting code..."
	uv run black tools_rag
	@echo "✓ Formatting completed"

