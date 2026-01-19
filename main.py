"""Main entry point for running Tools RAG evaluation."""

import argparse
from tools_rag.hybrid_tools_rag import ToolsRAG
from tools_rag.skills import ToolsSkills
from tools_rag.evaluation import evaluate_rag, evaluate_skills, compare_rag_vs_skills
from tools_rag.config import ToolsRAGConfig
from tools_rag.tools import tools
from tools_rag.questions import test_questions


def main():
    """Run evaluation in different modes."""
    parser = argparse.ArgumentParser(
        description="Evaluate tool selection: Hybrid RAG vs. LLM Skills"
    )
    parser.add_argument(
        "--mode",
        choices=["rag", "skills", "compare"],
        default="rag",
        help="Evaluation mode: rag (hybrid retrieval), skills (LLM-based), compare (both)",
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="OpenAI model for skills mode (default: gpt-4o-mini)",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=10,
        help="Number of tools to retrieve (default: 10)",
    )

    args = parser.parse_args()

    # Initialize configuration
    config = ToolsRAGConfig(top_k=args.k)

    if args.mode == "rag":
        # RAG mode only
        print("=" * 100)
        print("MODE: Hybrid RAG (Semantic + BM25)")
        print("=" * 100 + "\n")

        rag = ToolsRAG(config)
        print("Testing CRUD: Populating with first 50 tools...")
        rag.populate_tools(tools[:50])
        print("Testing CRUD: Adding remaining tools...")
        rag.add_tools(tools[50:])
        print(f"Total tools in system: {len(tools)}\n")

        evaluate_rag(rag, test_questions, config)

    elif args.mode == "skills":
        # Skills mode only
        print("=" * 100)
        print(f"MODE: LLM Skills ({args.model})")
        print("=" * 100 + "\n")

        skills = ToolsSkills(model=args.model)
        print("Populating skills with all tools...")
        skills.populate_tools(tools)
        print(f"Total tools in system: {len(tools)}\n")

        evaluate_skills(skills, test_questions, k=args.k)

    elif args.mode == "compare":
        # Comparison mode
        print("=" * 100)
        print(f"MODE: Comparison (Hybrid RAG vs. LLM Skills)")
        print("=" * 100 + "\n")

        # Initialize both systems
        rag = ToolsRAG(config)
        rag.populate_tools(tools)

        skills = ToolsSkills(model=args.model)
        skills.populate_tools(tools)

        print(f"Initialized both systems with {len(tools)} tools\n")

        compare_rag_vs_skills(rag, skills, test_questions, config)


if __name__ == "__main__":
    main()
