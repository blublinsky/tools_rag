"""Configuration for the Tools RAG system."""

from pydantic import BaseModel, Field


class ToolsRAGConfig(BaseModel):
    """Configuration for hybrid RAG retrieval parameters."""

    embed_model: str = Field(
        default="sentence-transformers/all-mpnet-base-v2",
        description="Sentence transformer model for embeddings",
    )

    alpha: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Weight for dense vs sparse retrieval (1.0 = full dense, 0.0 = full sparse)",
    )

    top_k: int = Field(
        default=10, ge=1, le=50, description="Number of tools to retrieve"
    )

    threshold: float = Field(
        default=0.01,
        ge=0.0,
        le=1.0,
        description="Minimum similarity threshold for filtering results",
    )

    filter_tools: bool = Field(
        default=True,
        description="Enable tool filtering. If False, returns all tools (no RAG filtering)",
    )
