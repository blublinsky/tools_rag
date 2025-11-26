"""Main entry point for running Tools RAG evaluation."""

from tools_rag.hybrid_tools_rag import ToolsRAG
from tools_rag.evaluation import evaluate_rag
from tools_rag.config import ToolsRAGConfig
from tools_rag.tools import tools
from tools_rag.questions import test_questions


if __name__ == "__main__":
    # Initialize ToolsRAG with default configuration
    config = ToolsRAGConfig()
    rag = ToolsRAG(config)

    # Test CRUD operations: populate with first 50 tools, then add the rest
    print("Testing CRUD: Populating with first 50 tools...")
    rag.populate_tools(tools[:50])

    print("Testing CRUD: Adding remaining tools...")
    rag.add_tools(tools[50:])
    print(f"Total tools in system: {len(tools)}\n")

    # Run evaluation
    evaluate_rag(rag, test_questions, config)
