"""Tests for ToolsRAG system."""

import pytest
from tools_rag.hybrid_tools_rag import ToolsRAG
from tools_rag.config import ToolsRAGConfig


class TestToolsRAG:
    """Test main ToolsRAG functionality."""

    @pytest.fixture(autouse=True)
    def cleanup_chroma(self):
        """Clean up ChromaDB before each test."""
        import chromadb

        client = chromadb.Client()
        try:
            client.delete_collection("tools")
        except:
            pass
        yield
        # Cleanup after test
        try:
            client.delete_collection("tools")
        except:
            pass

    @pytest.fixture
    def sample_tools(self):
        """Sample tools for testing."""
        return [
            {
                "name": "get_weather",
                "desc": "Get current weather conditions",
                "params": {"location": {"type": "string"}},
            },
            {
                "name": "get_forecast",
                "desc": "Get weather forecast",
                "params": {"location": {"type": "string"}},
            },
            {
                "name": "send_email",
                "desc": "Send an email message",
                "params": {"to": {"type": "string"}},
            },
            {
                "name": "search_wiki",
                "desc": "Search Wikipedia articles",
                "params": {"query": {"type": "string"}},
            },
            {
                "name": "calculate",
                "desc": "Perform mathematical calculations",
                "params": {"expression": {"type": "string"}},
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
        results = rag.retrieve_hybrid("What's the weather like?")

        assert len(results) <= 3  # top_k=3
        assert len(results) > 0
        assert all(isinstance(r, dict) for r in results)
        assert all("name" in r and "desc" in r for r in results)

        # Weather-related tools should be in results
        names = [r["name"] for r in results]
        assert "get_weather" in names or "get_forecast" in names

    def test_retrieve_hybrid_without_filtering(self, sample_tools):
        """Test retrieval with filtering disabled."""
        config = ToolsRAGConfig(filter_tools=False)
        rag = ToolsRAG(config)
        rag.populate_tools(sample_tools)

        results = rag.retrieve_hybrid("What's the weather like?")

        # Should return all tools
        assert len(results) == 5
        names = {r["name"] for r in results}
        assert names == {
            "get_weather",
            "get_forecast",
            "send_email",
            "search_wiki",
            "calculate",
        }

    def test_retrieve_with_custom_parameters(self, rag):
        """Test retrieval with custom k, alpha, threshold."""
        results = rag.retrieve_hybrid(
            "weather", k=2, alpha=0.5, threshold=0.0  # Override config
        )

        assert len(results) <= 2

    def test_add_tools(self, rag):
        """Test adding new tools dynamically."""
        new_tools = [
            {"name": "get_time", "desc": "Get current time", "params": {}},
            {"name": "set_alarm", "desc": "Set an alarm", "params": {}},
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
        text = rag._build_text(tool)

        assert "test_tool" in text
        assert "Test description" in text
        # Params should not be in text (optimized for performance)
        assert "arg" not in text

    def test_retrieve_sparse_scores(self, rag):
        """Test BM25 sparse scoring."""
        scores = rag._retrieve_sparse_scores("weather forecast")

        assert isinstance(scores, dict)
        assert len(scores) > 0
        assert all(0.0 <= score <= 1.0 for score in scores.values())

    def test_empty_retrieval(self):
        """Test retrieval on empty tool set - should not raise error."""
        config = ToolsRAGConfig(filter_tools=False)
        rag = ToolsRAG(config)
        # Don't populate any tools

        results = rag.retrieve_hybrid("test query")
        assert len(results) == 0

    def test_high_threshold_filtering(self, sample_tools):
        """Test that high threshold filters out results."""
        config = ToolsRAGConfig(top_k=10, threshold=0.99)  # Very high threshold
        rag_strict = ToolsRAG(config)
        rag_strict.populate_tools(
            [
                {
                    "name": "unrelated_tool",
                    "desc": "Completely unrelated xyz abc",
                    "params": {},
                }
            ]
        )

        results = rag_strict.retrieve_hybrid("weather forecast sunny day")
        # Should filter out low-similarity matches
        assert len(results) == 0

    def test_semantic_vs_keyword_matching(self, rag):
        """Test that hybrid retrieval combines semantic and keyword matching."""
        # Semantic query (no exact keyword match)
        semantic_results = rag.retrieve_hybrid("What's the temperature outside?")
        assert len(semantic_results) > 0

        # Keyword query (exact match)
        keyword_results = rag.retrieve_hybrid("get_weather")
        assert len(keyword_results) > 0
        assert keyword_results[0]["name"] == "get_weather"
