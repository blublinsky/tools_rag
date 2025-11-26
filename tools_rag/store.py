"""Vector store wrapper for ChromaDB."""

import chromadb


class ChromaStore:
    """Wrapper for ChromaDB vector database operations."""

    def __init__(self):
        """Initialize in-memory ChromaDB client and collection."""
        self.client = chromadb.Client()
        self.coll = self.client.get_or_create_collection(
            "tools", metadata={"hnsw:space": "cosine"}
        )

    def add(
        self,
        ids: list[str],
        docs: list[str],
        vectors: list[list[float]],
        metadatas: list[dict] | None = None,
    ) -> None:
        """Add documents with embeddings to the collection.

        Args:
            ids: List of unique identifiers for documents
            docs: List of document texts
            vectors: List of embedding vectors
            metadatas: Optional list of metadata dictionaries (e.g., full tool data)
        """
        self.coll.add(ids=ids, documents=docs, embeddings=vectors, metadatas=metadatas)

    def search_with_scores(
        self, vector: list[float], k: int
    ) -> tuple[list[str], list[float], list[dict]]:
        """Search and return IDs, similarity scores, and metadata.

        Args:
            vector: Query embedding vector
            k: Number of results to return

        Returns:
            Tuple of (document IDs, similarity scores, metadatas) where scores are 0-1 (1=most similar)
        """
        results = self.coll.query(
            query_embeddings=[vector], n_results=k, include=["metadatas", "distances"]
        )
        ids = results["ids"][0]
        distances = results["distances"][0]
        metadatas = results["metadatas"][0]
        # Convert cosine distance to similarity (1 - distance)
        # ChromaDB returns distances, lower is better, so we invert
        similarities = [1 - d for d in distances]
        return ids, similarities, metadatas

    def delete(self, ids: list[str]) -> None:
        """Delete documents from the collection.

        Args:
            ids: List of document IDs to delete
        """
        self.coll.delete(ids=ids)

    def get_all(self) -> dict:
        """Get all documents with their metadata.

        Returns:
            Dictionary with 'ids', 'documents', 'embeddings', and 'metadatas' keys
        """
        return self.coll.get()
