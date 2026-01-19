"""Evaluation functions for Tools RAG system."""

from pydantic import BaseModel, Field
from tools_rag.config import ToolsRAGConfig
from tools_rag.hybrid_tools_rag import ToolsRAG


class EvaluationResult(BaseModel):
    """Result of evaluating a single question."""

    question: str = Field(description="The question asked")
    expected: str | None = Field(
        description="Expected tool name, None for negative cases"
    )
    retrieved_names: list[str] = Field(description="List of retrieved tool names")
    rank: int = Field(
        description="Rank of expected tool (1-based), -1 if not found or negative case"
    )

    @property
    def is_negative(self) -> bool:
        """Whether this is a negative test case (no correct answer)."""
        return self.expected is None

    @property
    def is_hit(self) -> bool:
        """Whether the expected tool was found in results."""
        return self.rank > 0

    @property
    def retrieved_str(self) -> str:
        """Formatted string of retrieved tools."""
        return " → ".join(self.retrieved_names) if self.retrieved_names else "NONE"


def _calculate_rank(expected: str | None, retrieved: list[str]) -> int:
    """Calculate 1-based rank of expected tool in retrieved list.

    Args:
        expected: Expected tool name, None for negative cases
        retrieved: List of retrieved tool names

    Returns:
        1-based rank if found (1 = top result), -1 if not found or negative case
    """
    if expected is None:
        return -1  # Negative case: no correct answer exists

    try:
        return retrieved.index(expected) + 1  # Convert 0-based index to 1-based rank
    except ValueError:
        return -1  # Not found


def evaluate_rag(
    rag: ToolsRAG, test_questions: list[tuple[str, str | None]], config: ToolsRAGConfig
) -> None:
    """Evaluate the RAG system on a set of test questions.

    Args:
        rag: Initialized ToolsRAG instance
        test_questions: List of (question, expected_tool) tuples
        config: ToolsRAGConfig instance
    """
    print("Hybrid Tools RAG - Evaluation")
    print(
        f"Goal: Include correct tool in TOP_K={config.top_k} results for LLM selection"
    )
    print(
        f"Config: ALPHA={config.alpha}, THRESHOLD={config.threshold}, TOP_K={config.top_k}"
    )
    print(
        f"Test set: {len(test_questions)} questions ({sum(1 for _, t in test_questions if t is None)} negative cases)\n"
    )

    results: list[EvaluationResult] = []

    for i, (question, expected_tool) in enumerate(test_questions, 1):
        # Retrieve tools using hybrid search (returns dict[server: tools] or None)
        server_tools = rag.retrieve_hybrid(question)
        
        # Handle case where filtering is disabled (returns None)
        if server_tools is None:
            from tools_rag.tools import tools
            hybrid_ranked = tools
        else:
            # Flatten dict of server->tools to single list
            hybrid_ranked = [tool for tools_list in server_tools.values() for tool in tools_list]
        
        hybrid_names = [t["name"] for t in hybrid_ranked]

        # Calculate rank of expected tool in results
        hybrid_rank = _calculate_rank(expected_tool, hybrid_names)

        results.append(
            EvaluationResult(
                question=question,
                expected=expected_tool,
                retrieved_names=hybrid_names,
                rank=hybrid_rank,
            )
        )

    # Print results table
    print(
        f"{'#':<4} {'Expected Tool':<18} {'Retrieved (TOP-' + str(config.top_k) + ')':<60} {'✓':<3}"
    )
    print("=" * 85)

    for i, result in enumerate(results, 1):
        expected_str = result.expected if result.expected is not None else "NONE"
        symbol = "✓" if result.is_hit else "✗"

        print(f"{i:<4} {expected_str:<18} {result.retrieved_str:<60} {symbol:<3}")

    # Calculate metrics (only on positive cases)
    positive_results = [r for r in results if not r.is_negative]
    negative_results = [r for r in results if r.is_negative]

    total_positive = len(positive_results)
    hit_at_k = sum(1 for r in positive_results if r.is_hit)
    valid_ranks = [r.rank for r in positive_results if r.is_hit]
    avg_rank = sum(valid_ranks) / len(valid_ranks) if valid_ranks else 0

    # Print metrics
    print("\n" + "=" * 85)
    print("RETRIEVAL QUALITY METRICS:")
    print("=" * 85)
    print(
        f"Top-{config.top_k} Hit Rate:        {hit_at_k}/{total_positive} = {hit_at_k/total_positive:.1%}"
    )
    print(f"Avg Rank (when found):   {avg_rank:.2f}")
    print("=" * 85)
    print(f"✓ = Expected tool found in TOP_K={config.top_k} results")
    print("✗ = Expected tool NOT found (or negative case)\n")

    # Detailed analysis
    print("=" * 85)
    print("DETAILED ANALYSIS:")
    print("=" * 85)

    # Misses: Expected tool not in TOP_K
    misses = [r for r in positive_results if not r.is_hit]

    if misses:
        print(
            f"\n❌ MISSES: Expected tool NOT in TOP_K={config.top_k} ({len(misses)} case(s))\n"
        )
        for i, result in enumerate(misses, 1):
            print(f"{i}. Question: {result.question}")
            print(f"   Expected: {result.expected}")
            print(
                f"   Retrieved: {result.retrieved_str if result.retrieved_names else 'NONE (filtered by threshold)'}"
            )
            print()
    else:
        print(f"\n✅ PERFECT: All expected tools found in TOP_K={config.top_k}!\n")

    # Show negative case handling
    if negative_results:
        filtered_count = sum(1 for r in negative_results if not r.retrieved_names)
        print(
            f"⚠️  NEGATIVE CASES: {len(negative_results)} queries with no correct tool"
        )
        print(f"   Filtered by threshold: {filtered_count}/{len(negative_results)}")
        print(
            f"   Passed to LLM: {len(negative_results) - filtered_count}/{len(negative_results)} (LLM will handle)\n"
        )

    print("=" * 85)
