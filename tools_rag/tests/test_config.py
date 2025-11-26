"""Tests for ToolsRAGConfig."""

import pytest
from pydantic import ValidationError
from tools_rag.config import ToolsRAGConfig


class TestToolsRAGConfig:
    """Test configuration validation and defaults."""

    def test_default_config(self):
        """Test default configuration values."""
        config = ToolsRAGConfig()
        assert config.embed_model == "sentence-transformers/all-mpnet-base-v2"
        assert config.alpha == 0.8
        assert config.top_k == 10
        assert config.threshold == 0.01
        assert config.filter_tools is True

    def test_custom_config(self):
        """Test custom configuration values."""
        config = ToolsRAGConfig(
            embed_model="custom-model",
            alpha=0.5,
            top_k=20,
            threshold=0.1,
            filter_tools=False,
        )
        assert config.embed_model == "custom-model"
        assert config.alpha == 0.5
        assert config.top_k == 20
        assert config.threshold == 0.1
        assert config.filter_tools is False

    def test_alpha_validation(self):
        """Test alpha parameter validation (0.0-1.0)."""
        # Valid values
        ToolsRAGConfig(alpha=0.0)
        ToolsRAGConfig(alpha=0.5)
        ToolsRAGConfig(alpha=1.0)

        # Invalid values
        with pytest.raises(ValidationError):
            ToolsRAGConfig(alpha=-0.1)
        with pytest.raises(ValidationError):
            ToolsRAGConfig(alpha=1.1)

    def test_top_k_validation(self):
        """Test top_k parameter validation (>= 1, <= 50)."""
        # Valid values
        ToolsRAGConfig(top_k=1)
        ToolsRAGConfig(top_k=25)
        ToolsRAGConfig(top_k=50)

        # Invalid values
        with pytest.raises(ValidationError):
            ToolsRAGConfig(top_k=0)
        with pytest.raises(ValidationError):
            ToolsRAGConfig(top_k=51)

    def test_threshold_validation(self):
        """Test threshold parameter validation (0.0-1.0)."""
        # Valid values
        ToolsRAGConfig(threshold=0.0)
        ToolsRAGConfig(threshold=0.5)
        ToolsRAGConfig(threshold=1.0)

        # Invalid values
        with pytest.raises(ValidationError):
            ToolsRAGConfig(threshold=-0.1)
        with pytest.raises(ValidationError):
            ToolsRAGConfig(threshold=1.1)
