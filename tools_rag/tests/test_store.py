"""Tests for ChromaStore."""

import pytest
from tools_rag.store import ChromaStore


class TestChromaStore:
    """Test ChromaDB wrapper operations."""

    @pytest.fixture
    def store(self):
        """Create a fresh ChromaStore for each test."""
        # Create a unique store for each test to avoid conflicts
        import chromadb

        client = chromadb.Client()
        # Delete existing collection if it exists
        try:
            client.delete_collection("tools")
        except:
            pass
        return ChromaStore()

    @pytest.fixture
    def sample_tools(self):
        """Sample tools for testing."""
        return [
            {"name": "tool1", "desc": "First tool", "params": {}},
            {"name": "tool2", "desc": "Second tool", "params": {}},
            {"name": "tool3", "desc": "Third tool", "params": {}},
        ]

    def test_add_and_get_all(self, store, sample_tools):
        """Test adding documents and retrieving all."""
        import json

        ids = [t["name"] for t in sample_tools]
        docs = [f"{t['name']} {t['desc']}" for t in sample_tools]
        vectors = [[0.1, 0.2, 0.3] for _ in sample_tools]
        metadatas = [{"tool_json": json.dumps(t)} for t in sample_tools]

        store.add(ids, docs, vectors, metadatas)

        result = store.get_all()
        assert len(result["ids"]) == 3
        assert set(result["ids"]) == {"tool1", "tool2", "tool3"}
        assert len(result["documents"]) == 3
        assert len(result["metadatas"]) == 3

    def test_search_with_scores(self, store):
        """Test search with similarity scores."""
        import json

        tools = [
            {"name": "weather", "desc": "Get weather info"},
            {"name": "news", "desc": "Get latest news"},
        ]

        ids = [t["name"] for t in tools]
        docs = [f"{t['name']} {t['desc']}" for t in tools]
        vectors = [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
        metadatas = [{"tool_json": json.dumps(t)} for t in tools]

        store.add(ids, docs, vectors, metadatas)

        # Search with vector close to first tool
        query_vec = [0.9, 0.1, 0.0]
        result_ids, similarities, result_metadatas = store.search_with_scores(
            query_vec, k=2
        )

        assert len(result_ids) == 2
        assert result_ids[0] == "weather"  # Closest match
        assert similarities[0] > similarities[1]  # First is more similar
        assert len(result_metadatas) == 2
        assert "tool_json" in result_metadatas[0]

    def test_delete(self, store, sample_tools):
        """Test deleting documents."""
        import json

        ids = [t["name"] for t in sample_tools]
        docs = [f"{t['name']} {t['desc']}" for t in sample_tools]
        vectors = [[0.1, 0.2, 0.3] for _ in sample_tools]
        metadatas = [{"tool_json": json.dumps(t)} for t in sample_tools]

        store.add(ids, docs, vectors, metadatas)

        # Delete one tool
        store.delete(["tool2"])

        result = store.get_all()
        assert len(result["ids"]) == 2
        assert "tool2" not in result["ids"]
        assert set(result["ids"]) == {"tool1", "tool3"}

    def test_empty_store(self, store):
        """Test operations on empty store."""
        result = store.get_all()
        # Empty store returns empty lists, not error
        assert isinstance(result["ids"], list)
        assert isinstance(result["documents"], list)
