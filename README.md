# Tools RAG - Hybrid Retrieval for Tool Selection

A high-performance hybrid RAG (Retrieval Augmented Generation) system for intelligent tool selection in LLM applications. Combines dense (semantic) and sparse (BM25) retrieval to achieve **100% accuracy** on tool matching tasks.

## 🎯 Purpose

When your LLM has access to hundreds of tools, including all of them in the prompt is:
- **Expensive** - More tokens = higher cost
- **Slow** - Larger context = slower inference
- **Less accurate** - LLM struggles with too many options

**Solution:** Use hybrid RAG to pre-filter from 100+ tools down to the top 10 most relevant tools before the LLM sees them.

## 🔬 How It Works

### Hybrid Retrieval

Combines two complementary retrieval methods:

1. **Dense (Semantic) Retrieval**
   - Uses sentence-transformers embeddings
   - Captures semantic meaning
   - Good for natural language queries
   
   The query and each tool are encoded into high-dimensional vector representations using the `all-mpnet-base-v2` model. Tools are then ranked by cosine similarity between their embeddings and the query embedding stored in ChromaDB. This approach excels at understanding intent—for example, "What's the temperature outside?" matches `get_weather` even though they share no exact words. Semantic search naturally handles synonyms, paraphrasing, and contextual variations without requiring exact keyword matches.

2. **Sparse (BM25) Retrieval**
   - Tokenizes into individual words
   - Term frequency + inverse document frequency scoring
   - Excels at exact matches for technical terms
   
   BM25 (Best Matching 25) tokenizes the query and tools into individual words, then ranks tools based on term frequency (TF) and inverse document frequency (IDF). Tools containing exact query terms score higher, with adjustments for document length and term saturation. This approach excels at precise matching—for example, "get_weather function" will strongly match the `get_weather` tool because of the exact term overlap. Keyword search is particularly effective for technical names, function identifiers, and domain-specific terminology where exact matches are critical.

3. **Hybrid**
   - `final_score = alpha × dense_score + (1 - alpha) × sparse_score`
   - Rank-based scoring for stability
   - Threshold filtering for quality
   
   The hybrid approach fuses both retrieval scores using a weighted formula where `alpha` controls the balance. Each method produces a ranked list of tools, which are then converted to rank-based scores for stability. The final ranking combines these scores, ensuring that tools appearing high in either method (or both) rise to the top. This fusion mechanism provides robust retrieval that works equally well whether users phrase queries in natural language ("What's the temperature?") or use technical terminology ("get_weather API").

## ⚠️ Important: Tool Names as Identifiers

**Tool names must be unique.** Each tool is identified by its `name` field, which serves as the primary key in the system. If you add a tool with a name that already exists, it will overwrite the previous tool with that name. This is intentional behavior that enables the upsert functionality in CRUD operations.

**Best practices:**
- Use descriptive, unique names like `get_weather`, `send_email_v2`, `search_products_amazon`
- Avoid generic names like `search`, `get`, `update` that could conflict
- Include version suffixes if you need multiple variants (e.g., `translate_v1`, `translate_v2`)

## 🔄 Usage in LLM with Tools

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

## 🚀 Quick Start

### Common Commands

This project uses a Makefile to simplify common operations throughout the codebase. All commands referenced in this documentation are available via make:

```bash
# Install dependencies
make install

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

### Installation

```bash
make install
```

### Basic Usage

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
        "params": {"location": {"type": "string"}},
        "server": "weather-mcp"  # MCP server name
    },
    # ... more tools
]
rag.populate_tools(tools)

# 3. Retrieve relevant tools for a query
query = "What's the temperature outside?"
relevant_tools, servers = rag.retrieve_hybrid(query)
# Returns:
# - relevant_tools: [{"name": "get_weather", "desc": ..., "params": ...}, ...]
#   (without 'server' field)
# - servers: ["weather-mcp", ...]  # Unique server names needed
```

## 🛠️ CRUD Operations

In production environments, your tool catalog evolves—new tools are added, existing tools are updated with better descriptions, and deprecated tools are removed. CRUD operations allow you to manage these changes dynamically without application restart. 

### Add Tools

Add new tools or update existing ones (upsert behavior). If a tool with the same name already exists, it will be updated; otherwise, it will be added to the catalog.

```python
# Add new tools
new_tools = [
    {"name": "send_email", "desc": "Send an email", "params": {...}, "server": "communication-mcp"},
    {"name": "get_calendar", "desc": "Get calendar events", "params": {...}, "server": "productivity-mcp"}
]
rag.add_tools(new_tools)
```

### Remove Tools

Remove tools from the catalog by their names. The tools will be deleted from ChromaDB and the BM25 index will be rebuilt.

```python
# Remove tools by name
rag.remove_tools(["old_tool_1", "old_tool_2"])
```

**Note:** To completely repopulate your tool catalog, use `remove_tools()` to clear existing tools, then `add_tools()` to add the new set.

## 🔧 Configuration

The implementation is fully configurable using the `ToolsRAGConfig` Pydantic class, allowing you to tune the embedding model, retrieval weights, result filtering, and more.

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
  - `True` (default) - Returns `(tools, servers)` with top-K filtered results
  - `False` - Returns `(None, None)` to signal "use all tools"
  - When `False`, avoids expensive processing - caller should use their full tool list
  - Use for A/B testing RAG vs no-RAG, or debugging

## 🧪 Testing

The project includes comprehensive unit tests and an evaluation suite to measure retrieval quality.

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

### 📊 Performance
**Evaluation Output includes:**
- Hit rate metrics
- Average rank when found
- Detailed per-query results
- Negative case handling

Tested on 123 queries across 100 tools:

| Metric | Value |
|--------|-------|
| **Top-10 Hit Rate** | 100% (118/118) |
| **Average Rank** | 1.35 |
| **Retrieval Time** | 10-50ms |
| **Memory Footprint** | ~450MB (model + indices) |

### 📈 Optimization History

The current 100% hit rate was achieved through iterative improvements to the retrieval algorithm, embedding model selection, and tool descriptions:

| Optimization | Hit Rate | Notes |
|--------------|----------|-------|
| Dense only | 75% | Baseline |
| + BM25 fusion (α=0.5) | 80% | Better keyword matching |
| + Rank-based scoring | 85% | More stable |
| + Better embeddings | 96.5% | all-mpnet-base-v2 |
| + Optimized descriptions | 99.1% | Removed params from text |
| + Tool expansion (100) | 100% | Current state |

## 🦙 Integration with Llama Stack

### MCP Server Support

Tools RAG supports Model Context Protocol (MCP) servers. Each tool can specify which MCP server it belongs to:

```python
tools = [
    {
        "name": "get_weather",
        "desc": "Get current weather",
        "params": {...},
        "server": "weather-mcp"  # MCP server identifier
    },
    {
        "name": "send_email",
        "desc": "Send email",
        "params": {...},
        "server": "communication-mcp"
    }
]
```

When retrieving tools, you get both the tools AND the list of MCP servers needed:

```python
tools, servers = rag.retrieve_hybrid("What's the weather?")
# tools: [{"name": "get_weather", ...}]  # Clean, no 'server' field
# servers: ["weather-mcp"]  # Unique servers for these tools
```

### Implementation

Use Tools RAG as a **pre-processing step** before LLM inference to reduce context size:

```python
from llama_stack_client import LlamaStackClient
from tools_rag.hybrid_tools_rag import ToolsRAG
from tools_rag.config import ToolsRAGConfig

# Initialize once at startup
llama_client = LlamaStackClient()
tool_rag = ToolsRAG(ToolsRAGConfig(top_k=10))
tool_rag.populate_tools(all_100_tools)  # Tools with 'server' field

def process_request(user_query: str):
    # Step 1: RAG pre-filter (10-50ms)
    # Reduces 100 tools → 10 most relevant tools
    relevant_tools, mcp_servers = tool_rag.retrieve_hybrid(user_query)
    
    # Step 2: Configure MCP servers
    # Use the server list to authorize/configure required MCP servers
    for server in mcp_servers:
        llama_client.ensure_mcp_server_ready(server)
    
    # Step 3: Format for Llama Stack
    tools_for_llm = [
        {
            "name": t["name"],
            "description": t["desc"],
            "parameters": t["params"]
        }
        for t in relevant_tools
    ]
    
    # Step 4: Single LLM turn with filtered tools
    response = llama_client.inference.chat_completion(
        model="llama-3.1-70b",
        messages=[{"role": "user", "content": user_query}],
        tools=tools_for_llm,  # Only 10 instead of 100!
        stream=False
    )
    
    # Step 5: Execute tools selected by LLM
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

### Alternative: Prompt-Based Tool Filtering

If your Llama Stack setup doesn't support passing specific tools via the `tools` parameter, or if MCP servers expose all their tools automatically, you can use **prompt-based filtering** to instruct the LLM which tools to use:

```python
def process_request(user_query: str):
    # Step 1: RAG retrieval
    relevant_tools, mcp_servers = tool_rag.retrieve_hybrid(user_query, k=10)
    
    # Step 2: Build tool list for system prompt
    tool_descriptions = "\n".join([
        f"- {t['name']}: {t['desc']}" 
        for t in relevant_tools
    ])
    
    # Step 3: Inject allowed tools into system prompt
    system_prompt = f"""You have access to the following tools:

{tool_descriptions}

IMPORTANT: Only use the tools listed above. Do not use any other tools that may be available."""
    
    # Step 4: Call LLM with instruction
    response = llama_client.inference.chat_completion(
        model="llama-3.1-70b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        # All MCP servers are registered, but LLM instructed to use only specific tools
    )
    
    return response
```

**When to use this approach:**
- ✅ Llama Stack doesn't support per-request tool filtering
- ✅ MCP servers automatically expose all their tools
- ✅ You want LLM to be aware of tool restrictions
- ⚠️ Note: Relies on LLM instruction-following (not API-enforced)

## 🦜 Integration with LangChain

LangChain has native support for passing specific tools to agents, making it ideal for Tools RAG integration.

### Architecture: Lazy Population with Server Exclusion

**Key Concepts:**
1. **System-level MCP servers** - Always accessible (e.g., weather, wikipedia)
2. **User-level MCP servers** - Require user auth tokens (e.g., Gmail, Calendar)
3. **Lazy population** - Tools loaded on first request
4. **Server exclusion** - Filter out unauthorized servers per request

### Implementation

```python
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import Tool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from tools_rag.hybrid_tools_rag import ToolsRAG
from tools_rag.config import ToolsRAGConfig

# Global RAG instance
tool_rag = ToolsRAG(ToolsRAGConfig(top_k=10))
TOOLS_POPULATED = False

# MCP server configuration
MCP_CONFIG = {
    "weather-mcp": {"url": "...", "auth_type": "system"},
    "wikipedia-mcp": {"url": "...", "auth_type": "system"},
    "gmail-mcp": {"url": "...", "auth_type": "user"},
    "calendar-mcp": {"url": "...", "auth_type": "user"},
}

# System-level auth (headers from environment/config)
SYSTEM_AUTH = {
    "weather-mcp": {"Authorization": "Bearer <system-token>", "X-API-Key": "..."},
    "wikipedia-mcp": {"Authorization": "Bearer <system-token>"},
}

# Initialize your LLM of choice (examples)
# Option 1: OpenAI
# from langchain_openai import ChatOpenAI
# llm = ChatOpenAI(model="gpt-4", temperature=0)

# Option 2: Anthropic Claude
# from langchain_anthropic import ChatAnthropic
# llm = ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0)

# Option 3: Local Llama via Ollama
# from langchain_ollama import ChatOllama
# llm = ChatOllama(model="llama3.1", temperature=0)

# Option 4: Any other LangChain-compatible LLM
from langchain_openai import ChatOpenAI  # Replace with your choice
llm = ChatOpenAI(model="gpt-4", temperature=0)

def process_request(user_query: str, user_tokens: dict = None):
    global TOOLS_POPULATED
    
    # Step 1: Lazy populate on first request
    if not TOOLS_POPULATED:
        all_tools = []
        
        # Fetch from all known MCP servers (system + user)
        for server_name, config in MCP_CONFIG.items():
            try:
                if config["auth_type"] == "system":
                    auth = SYSTEM_AUTH[server_name]
                elif config["auth_type"] == "user" and user_tokens and server_name in user_tokens:
                    auth = user_tokens[server_name]
                else:
                    continue  # Skip user servers if no token
                
                server_tools = mcp_list_tools(config["url"], auth)
                all_tools.extend(server_tools)
            except Exception as e:
                print(f"Failed to load tools from {server_name}: {e}")
        
        tool_rag.populate_tools(all_tools)
        TOOLS_POPULATED = True
    
    # Dynamically add tools from MCP servers with auth headers in this request
    if user_tokens:
        new_tools = []
        for server_name, auth in user_tokens.items():
            if server_name in MCP_CONFIG:
                config = MCP_CONFIG[server_name]
                try:
                    server_tools = mcp_list_tools(config["url"], auth)
                    new_tools.extend(server_tools)
                except Exception as e:
                    print(f"Failed to load tools from {server_name}: {e}")
        
        if new_tools:
            tool_rag.add_tools(new_tools)  # Upsert: updates existing or adds new
    
    # Step 2: RAG retrieval - returns dict[server: tools]
    server_tools = tool_rag.retrieve_hybrid(user_query, k=10)
    
    # Step 2: Filter by authorized servers and build MCP configs
    authorized_server_tools = {}
    mcp_server_configs = {}
    
    for server_name, tools in server_tools.items():
        config = MCP_CONFIG.get(server_name)
        if not config:
            continue
        
        # Get appropriate auth
        if config["auth_type"] == "system":
            auth = SYSTEM_AUTH[server_name]
        else:  # user-level
            auth = user_tokens.get(server_name) if user_tokens else None
            if not auth:
                continue  # Skip if no auth available
        
        # Server is authorized, keep its tools
        authorized_server_tools[server_name] = tools
        mcp_server_configs[server_name] = {
            "url": config["url"],
            "auth": auth
        }
    
    # Flatten tools for LangChain
    relevant_tools = [tool for tools_list in authorized_server_tools.values() for tool in tools_list]
    
    # Step 4: Create LangChain tools dynamically
    langchain_tools = []
    for server_name, tools in authorized_server_tools.items():
        server_config = mcp_server_configs[server_name]
        
        for tool in tools:
            # Wrapper function with proper closure
            def make_tool_func(url, auth, tool_name):
                def tool_func(**kwargs):
                    return mcp_call_tool(url, tool_name, kwargs, auth)
                return tool_func
            
            langchain_tool = Tool(
                name=tool["name"],
                func=make_tool_func(server_config["url"], server_config["auth"], tool["name"]),
                description=tool["desc"]
            )
            langchain_tools.append(langchain_tool)
    
    # Step 5: Create and run agent (works with any LLM that supports tool calling)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Use the provided tools to answer questions."),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_tool_calling_agent(llm, langchain_tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=langchain_tools)
    
    result = agent_executor.invoke({"input": user_query})
    return result["output"]
```

**Note**: `create_tool_calling_agent` works with any LangChain LLM that supports tool/function calling (OpenAI, Anthropic Claude, Llama 3.1+, etc.). The LLM automatically formats tool calls according to its native format.

### Example MCP Helper Functions

```python
import requests

def mcp_list_tools(url: str, auth: dict = None, timeout: int = 30) -> list[dict]:
    """Get list of available tools from MCP server."""
    response = requests.get(
        f"{url}/tools",
        headers=auth or {},
        timeout=timeout
    )
    response.raise_for_status()
    return response.json()["tools"]

def mcp_call_tool(url: str, tool_name: str, parameters: dict, auth: dict = None, timeout: int = 30) -> str:
    """Call a tool on the MCP server."""
    response = requests.post(
        f"{url}/tools/{tool_name}",
        json=parameters,
        headers=auth or {},
        timeout=timeout
    )
    response.raise_for_status()
    return response.json()["result"]
```

### Benefits

- ✅ **Lazy loading** - Tools populated on first request (not at startup)
- ✅ **Server-level exclusion** - Filter unauthorized servers efficiently
- ✅ **Flexible auth** - System-level and user-level MCP servers
- ✅ **No state tracking** - Tools stay in RAG, exclusion at query time
- ✅ **Dynamic connections** - Only connect to servers needed for query

### Example Usage

```python
# Request from user without Gmail access
response = process_request(
    "What's the weather in Paris?",
    user_tokens={"calendar-mcp": {"Authorization": "Bearer user-calendar-token"}}
)
# Works: weather is system-level, Gmail tools excluded

# Request from user with Gmail access
response = process_request(
    "Send an email to John",
    user_tokens={
        "gmail-mcp": {"Authorization": "Bearer user-gmail-token"},
        "calendar-mcp": {"Authorization": "Bearer user-calendar-token"}
    }
)
# Works: Gmail tools included since user provided token
```

## 🤝 Contributing

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

### Key Files to Understand

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
