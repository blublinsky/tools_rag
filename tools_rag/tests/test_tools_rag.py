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
        results, servers = rag.retrieve_hybrid("What's the weather like?")

        assert len(results) <= 3  # top_k=3
        assert len(results) > 0
        assert all(isinstance(r, dict) for r in results)
        assert all("name" in r and "desc" in r for r in results)
        # Server field should be removed from tools
        assert all("server" not in r for r in results)

        # Should have server list
        assert isinstance(servers, list)
        assert len(servers) > 0

        # Weather-related tools should be in results
        names = [r["name"] for r in results]
        assert "get_weather" in names or "get_forecast" in names

    def test_retrieve_hybrid_without_filtering(self, sample_tools):
        """Test retrieval with filtering disabled."""
        config = ToolsRAGConfig(filter_tools=False)
        rag = ToolsRAG(config)
        rag.populate_tools(sample_tools)

        results, servers = rag.retrieve_hybrid("What's the weather like?")

        # Should return None to signal use all tools
        assert results is None
        assert servers is None

    def test_retrieve_with_custom_parameters(self, rag):
        """Test retrieval with custom k, alpha, threshold."""
        results, _servers = rag.retrieve_hybrid(
            "weather", k=2, alpha=0.5, threshold=0.0  # Override config
        )

        assert len(results) <= 2

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

        results, servers = rag.retrieve_hybrid("test query")
        assert results is None
        assert servers is None

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

        results, servers = rag_strict.retrieve_hybrid("weather forecast sunny day")
        # Should filter out low-similarity matches
        assert len(results) == 0
        assert len(servers) == 0

    def test_semantic_vs_keyword_matching(self, rag):
        """Test that hybrid retrieval combines semantic and keyword matching."""
        # Semantic query (no exact keyword match)
        semantic_results, _servers1 = rag.retrieve_hybrid("What's the temperature outside?")
        assert len(semantic_results) > 0

        # Keyword query (exact match)
        keyword_results, _servers2 = rag.retrieve_hybrid("get_weather")
        assert len(keyword_results) > 0
        assert keyword_results[0]["name"] == "get_weather"

    def test_exclude_servers(self, rag):
        """Test that exclude_servers parameter filters out tools from specific servers."""
        # Query that would normally return weather tools
        results_all, servers_all = rag.retrieve_hybrid("What's the weather?")
        assert len(results_all) > 0
        assert "weather-mcp" in servers_all

        # Same query but exclude weather-mcp server
        results_filtered, servers_filtered = rag.retrieve_hybrid(
            "What's the weather?",
            exclude_servers=["weather-mcp"]
        )

        # Should not return any weather tools
        assert "weather-mcp" not in servers_filtered
        weather_tools = [t for t in results_filtered if "weather" in t["name"].lower()]
        assert len(weather_tools) == 0
