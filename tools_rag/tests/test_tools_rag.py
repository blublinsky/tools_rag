"""Tests for ToolsRAG system."""

import chromadb
from chromadb.errors import NotFoundError
import pytest
from tools_rag.hybrid_tools_rag import ToolsRAG
from tools_rag.config import ToolsRAGConfig


class TestToolsRAG:
    """Test main ToolsRAG functionality."""

    @pytest.fixture(autouse=True)
    def cleanup_chroma(self):
        """Clean up ChromaDB before each test."""

        client = chromadb.Client()
        try:
            client.delete_collection("tools")
        except (ValueError, NotFoundError):
            pass
        yield
        # Cleanup after test
        try:
            client.delete_collection("tools")
        except (ValueError, NotFoundError):
            pass

    @pytest.fixture
    def sample_tools(self):
        """Sample tools for testing."""
        return [
            {
                "name": "get_weather",
                "desc": "Get current weather conditions",
                "params": {"location": {"type": "string"}},
                "server": "weather-mcp",
            },
            {
                "name": "get_forecast",
                "desc": "Get weather forecast",
                "params": {"location": {"type": "string"}},
                "server": "weather-mcp",
            },
            {
                "name": "send_email",
                "desc": "Send an email message",
                "params": {"to": {"type": "string"}},
                "server": "communication-mcp",
            },
            {
                "name": "search_wiki",
                "desc": "Search Wikipedia articles",
                "params": {"query": {"type": "string"}},
                "server": "wikipedia-mcp",
            },
            {
                "name": "calculate",
                "desc": "Perform mathematical calculations",
                "params": {"expression": {"type": "string"}},
                "server": "calculator-mcp",
            },
        ]

    @pytest.fixture
    def rag(self, sample_tools):
        """Create ToolsRAG instance with sample tools."""
        config = ToolsRAGConfig(top_k=3, threshold=0.01)
        rag_instance = ToolsRAG(config)
        rag_instance.populate_tools(sample_tools)
        return rag_instance

    def test_initialization(self):
        """Test ToolsRAG initialization."""
        config = ToolsRAGConfig()
        rag = ToolsRAG(config)

        assert rag.config == config
        assert rag.embedding_model is not None
        assert rag.store is not None
        assert rag.bm25 is None  # Not built until tools added

    def test_populate_tools(self, sample_tools):
        """Test populating tools."""
        config = ToolsRAGConfig()
        rag = ToolsRAG(config)
        rag.populate_tools(sample_tools)

        assert rag.bm25 is not None  # BM25 should be built

        # Verify tools in store
        all_data = rag.store.get_all()
        assert len(all_data["ids"]) == 5
        assert set(all_data["ids"]) == {
            "get_weather",
            "get_forecast",
            "send_email",
            "search_wiki",
            "calculate",
        }

    def test_retrieve_hybrid_with_filtering(self, rag):
        """Test hybrid retrieval with filtering enabled."""
        server_tools = rag.retrieve_hybrid("What's the weather like?")

        assert server_tools is not None
        assert isinstance(server_tools, dict)
        
        # Flatten to single list for assertions
        all_tools = [tool for tools_list in server_tools.values() for tool in tools_list]
        
        assert len(all_tools) <= 3  # top_k=3
        assert len(all_tools) > 0
        assert all(isinstance(r, dict) for r in all_tools)
        assert all("name" in r and "desc" in r for r in all_tools)
        # Server field should be removed from tools
        assert all("server" not in r for r in all_tools)

        # Should have servers as keys
        assert len(server_tools) > 0

        # Weather-related tools should be in results
        names = [r["name"] for r in all_tools]
        assert "get_weather" in names or "get_forecast" in names

    def test_retrieve_hybrid_without_filtering(self, sample_tools):
        """Test retrieval with filtering disabled."""
        config = ToolsRAGConfig(filter_tools=False)
        rag = ToolsRAG(config)
        rag.populate_tools(sample_tools)

        server_tools = rag.retrieve_hybrid("What's the weather like?")

        # Should return None to signal use all tools
        assert server_tools is None

    def test_retrieve_with_custom_parameters(self, rag):
        """Test retrieval with custom k, alpha, threshold."""
        server_tools = rag.retrieve_hybrid(
            "weather", k=2, alpha=0.5, threshold=0.0  # Override config
        )

        # Flatten to count all tools
        all_tools = [tool for tools_list in server_tools.values() for tool in tools_list]
        assert len(all_tools) <= 2

    def test_add_tools(self, rag):
        """Test adding new tools dynamically."""
        new_tools = [
            {"name": "get_time", "desc": "Get current time", "params": {}, "server": "time-mcp"},
            {"name": "set_alarm", "desc": "Set an alarm", "params": {}, "server": "time-mcp"},
        ]

        rag.add_tools(new_tools)

        # Verify new tools in store
        all_data = rag.store.get_all()
        assert len(all_data["ids"]) == 7  # 5 original + 2 new
        assert "get_time" in all_data["ids"]
        assert "set_alarm" in all_data["ids"]

    def test_add_tool_upsert(self, rag):
        """Test upsert behavior - adding a tool with existing name updates it."""
        updated_tool = {
            "name": "get_weather",
            "desc": "Get detailed weather with extended forecast",
            "params": {"location": {"type": "string"}},
            "server": "weather-mcp",
        }

        rag.add_tools([updated_tool])

        # Should still have 5 tools (not 6)
        all_data = rag.store.get_all()
        assert len(all_data["ids"]) == 5

    def test_remove_tools(self, rag):
        """Test removing tools."""
        rag.remove_tools(["send_email", "calculate"])

        # Verify tools removed
        all_data = rag.store.get_all()
        assert len(all_data["ids"]) == 3
        assert "send_email" not in all_data["ids"]
        assert "calculate" not in all_data["ids"]

    def test_build_text(self, rag):
        """Test text representation building."""
        tool = {
            "name": "test_tool",
            "desc": "Test description",
            "params": {"arg": {"type": "string"}},
        }
        text = rag._build_text(tool)  # pylint: disable=protected-access

        assert "test_tool" in text
        assert "Test description" in text
        # Params should not be in text (optimized for performance)
        assert "arg" not in text

    def test_retrieve_sparse_scores(self, rag):
        """Test BM25 sparse scoring."""
        scores = rag._retrieve_sparse_scores("weather forecast")  # pylint: disable=protected-access

        assert isinstance(scores, dict)
        assert len(scores) > 0
        assert all(0.0 <= score <= 1.0 for score in scores.values())

    def test_empty_retrieval(self):
        """Test retrieval on empty tool set - should not raise error."""
        config = ToolsRAGConfig(filter_tools=False)
        rag = ToolsRAG(config)
        # Don't populate any tools

        server_tools = rag.retrieve_hybrid("test query")
        assert server_tools is None

    def test_high_threshold_filtering(self):
        """Test that high threshold filters out results."""
        config = ToolsRAGConfig(top_k=10, threshold=0.99)  # Very high threshold
        rag_strict = ToolsRAG(config)
        rag_strict.populate_tools(
            [
                {
                    "name": "unrelated_tool",
                    "desc": "Completely unrelated xyz abc",
                    "params": {},
                    "server": "test-mcp",
                }
            ]
        )

        server_tools = rag_strict.retrieve_hybrid("weather forecast sunny day")
        # Should filter out low-similarity matches
        assert len(server_tools) == 0

    def test_semantic_vs_keyword_matching(self, rag):
        """Test that hybrid retrieval combines semantic and keyword matching."""
        # Semantic query (no exact keyword match)
        semantic_server_tools = rag.retrieve_hybrid("What's the temperature outside?")
        semantic_results = [tool for tools_list in semantic_server_tools.values() for tool in tools_list]
        assert len(semantic_results) > 0

        # Keyword query (exact match)
        keyword_server_tools = rag.retrieve_hybrid("get_weather")
        keyword_results = [tool for tools_list in keyword_server_tools.values() for tool in tools_list]
        assert len(keyword_results) > 0
        assert keyword_results[0]["name"] == "get_weather"

    def test_server_filtering(self, rag):
        """Test that caller can filter tools by server."""
        # Query that would normally return weather tools
        server_tools = rag.retrieve_hybrid("What's the weather?")
        assert len(server_tools) > 0
        assert "weather-mcp" in server_tools

        # Caller can filter by authorized servers
        authorized_servers = ["communication-mcp", "wikipedia-mcp", "calculator-mcp"]
        filtered_tools = {
            server: tools 
            for server, tools in server_tools.items() 
            if server in authorized_servers
        }

        # Should not have weather-mcp server
        assert "weather-mcp" not in filtered_tools
