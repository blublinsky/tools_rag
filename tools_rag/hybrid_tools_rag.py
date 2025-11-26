"""Hybrid Tools RAG implementation"""

import json
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from tools_rag.store import ChromaStore
from tools_rag.config import ToolsRAGConfig


class ToolsRAG:
    """Hybrid RAG system for tool retrieval using dense and sparse methods."""

    def __init__(self, cfg: ToolsRAGConfig):
        """Initialize the ToolsRAG system with configuration.

        Args:
            cfg: ToolsRAGConfig instance with retrieval parameters
        """
        self.config = cfg
        self.embedding_model = SentenceTransformer(cfg.embed_model)
        self.store = ChromaStore()
        self.bm25 = None

    def populate_tools(self, tools_list: list[dict]) -> None:
        """Populate the RAG system with tools.

        Args:
            tools_list: List of tool dictionaries with 'name', 'desc', and 'params'
        """
        # Build text representations
        dense_docs = [self._build_text(t) for t in tools_list]

        # Serialize tool metadata to JSON strings (ChromaDB doesn't support nested dicts)
        metadatas = [{"tool_json": json.dumps(t)} for t in tools_list]

        # Create embeddings and store in ChromaDB with full tool metadata
        vectors = [self.embedding_model.encode(d).tolist() for d in dense_docs]
        self.store.add(
            [t["name"] for t in tools_list], dense_docs, vectors, metadatas=metadatas
        )

        # Rebuild BM25 from ChromaDB
        self._rebuild_bm25()

    def add_tools(self, new_tools: list[dict]) -> None:
        """Add or update tools (upsert).

        ChromaDB automatically handles upsert - if a tool with the same name exists,
        it will be updated. Otherwise, it will be added.

        Args:
            new_tools: List of tool dictionaries to add or update
        """
        # Build text representations
        dense_docs = [self._build_text(t) for t in new_tools]

        # Serialize tool metadata to JSON strings
        metadatas = [{"tool_json": json.dumps(t)} for t in new_tools]

        # Create embeddings and store in ChromaDB (upsert with full tool metadata)
        vectors = [self.embedding_model.encode(d).tolist() for d in dense_docs]
        self.store.add(
            [t["name"] for t in new_tools], dense_docs, vectors, metadatas=metadatas
        )

        # Rebuild BM25 from ChromaDB
        self._rebuild_bm25()

    def remove_tools(self, tool_names: list[str]) -> None:
        """Remove tools by name.

        Args:
            tool_names: List of tool names to remove
        """
        # Delete from ChromaDB
        self.store.delete(tool_names)

        # Rebuild BM25 from ChromaDB
        self._rebuild_bm25()

    def _rebuild_bm25(self) -> None:
        """Rebuild BM25 index from ChromaDB documents."""
        # Get all documents from ChromaDB
        all_data = self.store.get_all()
        if not all_data["documents"]:
            self.bm25 = None
            return

        # Build BM25 from documents (already in text representation)
        sparse_docs = [doc.split() for doc in all_data["documents"]]
        self.bm25 = BM25Okapi(sparse_docs)

    def retrieve_hybrid(
        self,
        query: str,
        k: int | None = None,
        alpha: float | None = None,
        threshold: float | None = None,
    ) -> list[dict]:
        """Retrieve tools based on dense and sparse embeddings (hybrid).

        Args:
            query: The query string to search for
            k: Number of tools to retrieve (uses config.top_k if None)
            alpha: Weight for dense vs sparse (uses config.alpha if None)
            threshold: Minimum similarity threshold (uses config.threshold if None)

        Returns:
            List of tool dictionaries filtered by threshold (or all tools if filter_tools=False)
        """
        # If filtering disabled, return all tools
        if not self.config.filter_tools:
            all_data = self.store.get_all()
            if not all_data["metadatas"]:
                return []
            return [json.loads(meta["tool_json"]) for meta in all_data["metadatas"]]

        # Use config defaults if not specified
        k = k if k is not None else self.config.top_k
        alpha = alpha if alpha is not None else self.config.alpha
        threshold = threshold if threshold is not None else self.config.threshold

        # Encode query
        q_vec = self.embedding_model.encode(query).tolist()

        # Dense (semantic) - rank-based scoring with actual similarities and metadata
        dense_ids, dense_similarities, dense_metadatas = self.store.search_with_scores(
            q_vec, k
        )
        dense_scores = {t: 1.0 - i / k for i, t in enumerate(dense_ids)}

        # Create lookup dictionaries from dense results
        similarity_lookup = dict(zip(dense_ids, dense_similarities))
        metadata_lookup = {
            id: json.loads(meta["tool_json"])
            for id, meta in zip(dense_ids, dense_metadatas)
        }

        # Sparse (BM25) - normalized to 0-1 range
        sparse_scores = self._retrieve_sparse_scores(query)
        sparse_ids = sorted(sparse_scores, key=sparse_scores.get, reverse=True)[:k]

        # Fusion (alpha * dense + (1-alpha) * sparse)
        fused = {}
        for t in set(dense_ids + sparse_ids):
            d = dense_scores.get(t, 0)
            s = sparse_scores.get(t, 0)
            fused[t] = alpha * d + (1 - alpha) * s
        final = sorted(fused, key=fused.get, reverse=True)[:k]

        # Filter by threshold using actual similarity scores
        # Only tools from dense results have similarity scores; BM25-only tools get 0.0
        filtered_results = []
        for name in final:
            sim = similarity_lookup.get(name, 0.0)
            if sim >= threshold and name in metadata_lookup:
                # Tool passed threshold and has metadata (from dense search)
                filtered_results.append(metadata_lookup[name])
            elif sim >= threshold:
                # Tool passed threshold but no metadata yet - shouldn't happen since
                # threshold filtering only applies to dense results, but handle gracefully
                pass

        return filtered_results

    def _build_text(self, t: dict) -> str:
        """Build text representation: name + desc only (best performance: 99.1% hit rate)."""
        return f"{t['name']} {t['desc']}"

    def _retrieve_sparse_scores(self, query: str) -> dict[str, float]:
        """Retrieve BM25 scores (normalized to 0-1 range).

        Args:
            query: The query string

        Returns:
            Dictionary mapping tool names to normalized scores
        """
        if self.bm25 is None:
            return {}

        # Get all tools from ChromaDB to maintain order consistency with BM25
        all_data = self.store.get_all()
        tool_names = all_data["ids"]

        sparse_scores_raw = self.bm25.get_scores(query.split())
        max_score = max(sparse_scores_raw) if max(sparse_scores_raw) > 0 else 1
        return {name: s / max_score for name, s in zip(tool_names, sparse_scores_raw)}
