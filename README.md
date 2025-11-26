# Tools RAG - Hybrid Retrieval for Tool Selection

A high-performance hybrid RAG (Retrieval Augmented Generation) system for intelligent tool selection in LLM applications. Combines dense (semantic) and sparse (BM25) retrieval to achieve **100% accuracy** on tool matching tasks.

## 🎯 Purpose

When your LLM has access to hundreds of tools, including all of them in the prompt is:
- **Expensive** - More tokens = higher cost
- **Slow** - Larger context = slower inference
- **Less accurate** - LLM struggles with too many options

**Solution:** Use hybrid RAG to pre-filter from 100+ tools down to the top 10 most relevant tools before the LLM sees them.

## 🚀 Quick Start

### Installation

Using uv (recommended):

```bash
# Install dependencies
make install

# Or manually with uv
uv sync --all-extras
```

Using pip:

```bash
pip install -e .
```

### Basic Usage (Library Mode)

```python
from tools_rag.hybrid_tools_rag import ToolsRAG
from tools_rag.config import ToolsRAGConfig

# 1. Initialize RAG system
config = ToolsRAGConfig(
    alpha=0.8,        # 80% semantic, 20% keyword matching
    top_k=10,         # Return top 10 tools
    threshold=0.01    # Minimum similarity threshold
)
rag = ToolsRAG(config)

# 2. Populate with your tools
tools = [
    {
        "name": "get_weather",
        "desc": "Get current weather conditions for a location",
        "params": {"location": {"type": "string"}}
    },
    # ... more tools
]
rag.populate_tools(tools)

# 3. Retrieve relevant tools for a query
query = "What's the temperature outside?"
relevant_tools = rag.retrieve_hybrid(query)
# Returns: [{"name": "get_weather", "desc": ..., "params": ...}, ...]
```

## 🦙 Integration with Llama Stack

### Pre-Filter Pattern (Recommended)

Use Tools RAG as a **pre-processing step** before LLM inference to reduce context size:

```python
from llama_stack_client import LlamaStackClient
from tools_rag.hybrid_tools_rag import ToolsRAG
from tools_rag.config import ToolsRAGConfig

# Initialize once at startup
llama_client = LlamaStackClient()
tool_rag = ToolsRAG(ToolsRAGConfig(top_k=10))
tool_rag.populate_tools(all_100_tools)

def process_request(user_query: str):
    # Step 1: RAG pre-filter (10-50ms)
    # Reduces 100 tools → 10 most relevant tools
    relevant_tools = tool_rag.retrieve_hybrid(user_query)
    
    # Step 2: Format for Llama Stack
    tools_for_llm = [
        {
            "name": t["name"],
            "description": t["desc"],
            "parameters": t["params"]
        }
        for t in relevant_tools
    ]
    
    # Step 3: Single LLM turn with filtered tools
    response = llama_client.inference.chat_completion(
        model="llama-3.1-70b",
        messages=[{"role": "user", "content": user_query}],
        tools=tools_for_llm,  # Only 10 instead of 100!
        stream=False
    )
    
    # Step 4: Execute tools selected by LLM
    if response.tool_calls:
        return execute_tools(response.tool_calls)
    
    return response
```

### Benefits

- ✅ **90% token reduction** - 10 tools vs 100 in context
- ✅ **Faster inference** - Smaller prompt = faster LLM
- ✅ **Lower cost** - Fewer input tokens
- ✅ **Better accuracy** - LLM focuses on relevant tools only
- ✅ **No extra turn** - RAG runs during same request

### Architecture

```
User Query
    ↓
[Tools RAG Pre-Filter]  ← 10-50ms, reduces 100 → 10 tools
    ↓
[LLM Tool Selection]    ← 200-500ms, picks 1-3 tools
    ↓
[Tool Execution]
    ↓
Response
```

## 📊 Performance

Tested on 123 queries across 100 tools:

| Metric | Value |
|--------|-------|
| **Top-10 Hit Rate** | 100% (118/118) |
| **Average Rank** | 1.35 |
| **Retrieval Time** | 10-50ms |
| **Memory Footprint** | ~450MB (model + indices) |

## 🔧 Configuration

```python
class ToolsRAGConfig:
    embed_model: str = "sentence-transformers/all-mpnet-base-v2"
    alpha: float = 0.8          # Dense vs sparse weight (0.0-1.0)
    top_k: int = 10             # Number of tools to return
    threshold: float = 0.01     # Minimum similarity score
    filter_tools: bool = True   # Enable/disable filtering
```

### Parameter Tuning

- **`alpha`**: Higher = more semantic, lower = more keyword-based
  - `0.8` (default) works well for natural language queries
  - `0.5` for mixed semantic/keyword queries
  - `0.2` for technical/exact term matching

- **`top_k`**: Number of tools to return
  - `10` (default) balances coverage and LLM context
  - Increase for complex multi-tool tasks
  - Decrease for simpler use cases

- **`threshold`**: Minimum similarity score
  - `0.01` (default) lets LLM handle borderline cases
  - Increase to filter more aggressively

- **`filter_tools`**: Enable/disable RAG filtering
  - `True` (default) - Returns top-K filtered tools
  - `False` - Returns **all tools** (no filtering, no ChromaDB query)
  - Use `False` to bypass RAG and let LLM see all tools (useful for A/B testing or debugging)

### Example: A/B Testing RAG vs No RAG

```python
# Test with RAG filtering
config_with_rag = ToolsRAGConfig(filter_tools=True, top_k=10)
rag = ToolsRAG(config_with_rag)
rag.populate_tools(tools)
filtered = rag.retrieve_hybrid("What's the weather?")
print(f"With RAG: {len(filtered)} tools")  # Returns 10 tools

# Test without RAG filtering (all tools)
config_no_rag = ToolsRAGConfig(filter_tools=False)
rag_no_filter = ToolsRAG(config_no_rag)
rag_no_filter.populate_tools(tools)
all_tools = rag_no_filter.retrieve_hybrid("What's the weather?")
print(f"Without RAG: {len(all_tools)} tools")  # Returns 100 tools
```

## 🛠️ CRUD Operations

### Add Tools Dynamically

```python
# Add new tools without rebuilding from scratch
new_tools = [
    {"name": "send_email", "desc": "Send an email", "params": {...}},
    {"name": "get_calendar", "desc": "Get calendar events", "params": {...}}
]
rag.add_tools(new_tools)
```

### Remove Tools

```python
# Remove tools by name
rag.remove_tools(["old_tool_1", "old_tool_2"])
```

### Update Tools

```python
# Update = add with same name (upsert)
updated_tool = {
    "name": "get_weather",
    "desc": "Get current weather with extended forecast",
    "params": {...}
}
rag.add_tools([updated_tool])
```

## 📁 Project Structure

```
Tools-RAG/
├── main.py                    # Entry point for evaluation
├── tools_rag/                 # Core library
│   ├── __init__.py               # Package exports
│   ├── hybrid_tools_rag.py       # Main ToolsRAG class
│   ├── store.py                  # ChromaDB wrapper
│   ├── config.py                 # Pydantic configuration
│   ├── tools.py                  # Tool definitions (100 tools)
│   ├── questions.py              # Test questions (120 queries)
│   ├── evaluation.py             # Evaluation utilities
│   └── tests/                    # Unit tests
│       ├── test_config.py           # Config tests
│       ├── test_store.py            # Store tests
│       └── test_tools_rag.py        # RAG tests
├── pyproject.toml             # Project metadata & dependencies (uv)
├── requirements.txt           # Legacy pip requirements
├── pytest.ini                 # Pytest configuration
├── .pylintrc                  # Pylint configuration
├── Makefile                   # Common development tasks
└── README.md
```

## 🔬 How It Works

### Hybrid Retrieval

Combines two complementary retrieval methods:

1. **Dense (Semantic) Retrieval**
   - Uses sentence-transformers embeddings
   - Captures semantic meaning
   - Good for natural language queries

2. **Sparse (BM25) Retrieval**
   - Keyword-based matching
   - Exact term matching
   - Good for technical terms

3. **Fusion**
   - `final_score = alpha × dense_score + (1 - alpha) × sparse_score`
   - Rank-based scoring for stability
   - Threshold filtering for quality

### Why Hybrid?

| Method | "What's the weather?" | "get_weather function" |
|--------|----------------------|------------------------|
| Dense only | ✅ Excellent | ⚠️ May miss exact match |
| Sparse only | ⚠️ Weak semantic match | ✅ Perfect keyword match |
| **Hybrid** | ✅ **Best of both** | ✅ **Best of both** |

## 🧪 Testing

### Using Makefile (Recommended)

```bash
# Run the evaluation suite
make run

# Run unit tests
make test

# Run tests with coverage
make test-coverage

# Run linter
make lint

# Format code
make format

# Clean up cache files
make clean

# See all available commands
make help
```

### Manual Testing

Run the evaluation suite:

```bash
python main.py
# or
make run
```

Output includes:
- Hit rate metrics
- Average rank when found
- Detailed per-query results
- Negative case handling

### Unit Tests

Run unit tests with pytest:

```bash
# Run all tests
pytest tools_rag/tests/ -v

# Run with coverage
pytest tools_rag/tests/ --cov=tools_rag --cov-report=html

# Run specific test file
pytest tools_rag/tests/test_tools_rag.py -v
```

**Test Coverage:**
- ✅ **Config validation** - 5 tests (100% coverage)
- ✅ **ChromaStore operations** - 4 tests (100% coverage)  
- ✅ **ToolsRAG functionality** - 13 tests (85% coverage)
- ✅ **22 tests total**, all passing

## 🏗️ Architecture Decisions

### Library vs Service

**Current: Library Mode** (recommended for <1000 tools)

**Pros:**
- ✅ Lowest latency (no network hop)
- ✅ Simple deployment
- ✅ Type-safe Python API

**When to consider microservice:**
- Multiple services need tool retrieval
- >1000 tools (>2GB memory)
- Frequent tool updates
- Independent scaling needs

### ChromaDB as Single Source of Truth

- Tool metadata stored in ChromaDB (as JSON)
- BM25 rebuilt from ChromaDB documents
- No separate tool list in memory
- CRUD operations update ChromaDB → rebuild indices

### Design Principles

1. **Simplicity** - Clean class-based design, minimal dependencies
2. **Performance** - Optimized for <50ms retrieval
3. **Accuracy** - 100% hit rate on test suite
4. **Flexibility** - Configurable via Pydantic, supports CRUD
5. **Production-ready** - Type hints, docstrings, error handling

## 📈 Optimization History

| Optimization | Hit Rate | Notes |
|--------------|----------|-------|
| Dense only | 75% | Baseline |
| + BM25 fusion (α=0.5) | 80% | Better keyword matching |
| + Rank-based scoring | 85% | More stable |
| + Better embeddings | 96.5% | all-mpnet-base-v2 |
| + Optimized descriptions | 99.1% | Removed params from text |
| + Tool expansion (100) | 100% | Current state |

## 🛠️ Development

### Setup Development Environment

```bash
# Install with dev dependencies
make install

# This installs:
# - Core: rank-bm25, chromadb, sentence-transformers, pydantic
# - Dev: pytest, pytest-cov, black, pylint
```

### Code Quality

```bash
# Run linter (pylint)
make lint

# Format code (black)
make format

# Run tests with coverage
make test-coverage
```

### Project Configuration

- **`pyproject.toml`** - Python project metadata, dependencies, build config
- **`.pylintrc`** - Code quality rules (max line length: 120, enforces docstrings)
- **`pytest.ini`** - Test configuration
- **`Makefile`** - Development commands

## 🤝 Contributing

Key files to understand:
- `tools_rag/hybrid_tools_rag.py` - Core retrieval logic
- `tools_rag/store.py` - Vector database abstraction
- `tools_rag/evaluation.py` - Metrics and testing
- `main.py` - Entry point for running evaluation

### Import Structure

```python
# For external users (recommended)
from tools_rag import ToolsRAG, ToolsRAGConfig, ChromaStore

# For direct module access
from tools_rag.config import ToolsRAGConfig
from tools_rag.store import ChromaStore
from tools_rag.hybrid_tools_rag import ToolsRAG
from tools_rag.evaluation import evaluate_rag

# All imports use absolute paths from tools_rag package
```

## 📝 License

MIT

## 🔗 Related

- [Llama Stack](https://github.com/meta-llama/llama-stack) - LLM application framework
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Sentence Transformers](https://www.sbert.net/) - Embedding models
- [Rank-BM25](https://github.com/dorianbrown/rank_bm25) - BM25 implementation

