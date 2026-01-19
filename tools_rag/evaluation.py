"""Evaluation functions for Tools RAG system."""

import time
from pydantic import BaseModel, Field
from tools_rag.config import ToolsRAGConfig
from tools_rag.hybrid_tools_rag import ToolsRAG
from tools_rag.skills import ToolsSkills


def _get_model_pricing(model: str) -> tuple[float, float]:
    """Get pricing for OpenAI models in dollars per million tokens.

    Args:
        model: Model name (e.g., "gpt-4o", "gpt-4o-mini")

    Returns:
        Tuple of (input_price_per_M, output_price_per_M)
    """
    pricing = {
        "gpt-4o": (2.50, 10.00),
        "gpt-4o-mini": (0.15, 0.60),
        "gpt-4-turbo": (10.00, 30.00),
        "gpt-4": (30.00, 60.00),
    }
    # Default to gpt-4o-mini pricing if unknown
    return pricing.get(model, pricing["gpt-4o-mini"])


def _calculate_query_cost(model: str, input_tokens: int = 4000, output_tokens: int = 100) -> float:
    """Calculate cost for a single query.

    Args:
        model: Model name
        input_tokens: Estimated input tokens (default: 4000 for 100 tools)
        output_tokens: Estimated output tokens (default: 100)

    Returns:
        Cost in dollars
    """
    input_price, output_price = _get_model_pricing(model)
    return (input_tokens * input_price + output_tokens * output_price) / 1_000_000


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


def evaluate_skills(
    skills: ToolsSkills, test_questions: list[tuple[str, str | None]], k: int = 10
) -> None:
    """Evaluate the Skills (LLM-based) system on a set of test questions.

    Args:
        skills: Initialized ToolsSkills instance
        test_questions: List of (question, expected_tool) tuples
        k: Number of tools to retrieve
    """
    print("LLM-Based Skills - Evaluation")
    print(f"Goal: Include correct tool in TOP_K={k} results for LLM selection")
    print(f"Model: {skills.model}")
    print(
        f"Test set: {len(test_questions)} questions ({sum(1 for _, t in test_questions if t is None)} negative cases)\n"
    )

    results: list[EvaluationResult] = []
    total_time = 0.0
    total_cost = 0.0

    for i, (question, expected_tool) in enumerate(test_questions, 1):
        # Retrieve tools using LLM (returns dict[server: tools] or None)
        start_time = time.time()
        server_tools = skills.retrieve_skills(question, k=k)
        elapsed = time.time() - start_time
        total_time += elapsed

        # Calculate cost based on actual model
        query_cost = _calculate_query_cost(skills.model)
        total_cost += query_cost

        # Handle case where filtering is disabled (returns None)
        if server_tools is None:
            from tools_rag.tools import tools

            skills_ranked = tools
        else:
            # Flatten dict of server->tools to single list
            skills_ranked = [
                tool for tools_list in server_tools.values() for tool in tools_list
            ]

        skills_names = [t["name"] for t in skills_ranked]

        # Calculate rank of expected tool in results
        skills_rank = _calculate_rank(expected_tool, skills_names)

        results.append(
            EvaluationResult(
                question=question,
                expected=expected_tool,
                retrieved_names=skills_names,
                rank=skills_rank,
            )
        )

    # Print results table
    print(f"{'#':<4} {'Expected Tool':<18} {'Retrieved (TOP-' + str(k) + ')':<60} {'✓':<3}")
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
    print(f"Top-{k} Hit Rate:        {hit_at_k}/{total_positive} = {hit_at_k/total_positive:.1%}")
    print(f"Avg Rank (when found):   {avg_rank:.2f}")
    print(f"Total Latency:           {total_time:.2f}s")
    print(f"Avg Latency per Query:   {total_time/len(test_questions)*1000:.0f}ms")
    print(f"Estimated Total Cost:    ${total_cost:.4f}")
    print("=" * 85)
    print(f"✓ = Expected tool found in TOP_K={k} results")
    print("✗ = Expected tool NOT found (or negative case)\n")

    # Detailed analysis
    print("=" * 85)
    print("DETAILED ANALYSIS:")
    print("=" * 85)

    # Misses: Expected tool not in TOP_K
    misses = [r for r in positive_results if not r.is_hit]

    if misses:
        print(f"\n❌ MISSES: Expected tool NOT in TOP_K={k} ({len(misses)} case(s))\n")
        for i, result in enumerate(misses, 1):
            print(f"{i}. Question: {result.question}")
            print(f"   Expected: {result.expected}")
            print(f"   Retrieved: {result.retrieved_str if result.retrieved_names else 'NONE'}")
            print()
    else:
        print(f"\n✅ PERFECT: All expected tools found in TOP_K={k}!\n")

    # Show negative case handling
    if negative_results:
        filtered_count = sum(1 for r in negative_results if not r.retrieved_names)
        print(f"⚠️  NEGATIVE CASES: {len(negative_results)} queries with no correct tool")
        print(f"   Filtered: {filtered_count}/{len(negative_results)}")
        print(
            f"   Passed to LLM: {len(negative_results) - filtered_count}/{len(negative_results)}\n"
        )

    print("=" * 85)


def compare_rag_vs_skills(
    rag: ToolsRAG,
    skills: ToolsSkills,
    test_questions: list[tuple[str, str | None]],
    config: ToolsRAGConfig,
) -> None:
    """Compare RAG and Skills approaches side-by-side.

    Args:
        rag: Initialized ToolsRAG instance
        skills: Initialized ToolsSkills instance
        test_questions: List of (question, expected_tool) tuples
        config: ToolsRAGConfig instance
    """
    print("=" * 100)
    print("COMPARISON: Hybrid RAG vs. LLM Skills")
    print("=" * 100)
    print(
        f"Test set: {len(test_questions)} questions ({sum(1 for _, t in test_questions if t is None)} negative)\n"
    )

    rag_results: list[EvaluationResult] = []
    skills_results: list[EvaluationResult] = []

    rag_time = 0.0
    skills_time = 0.0
    skills_cost = 0.0

    # Evaluate both approaches
    for question, expected_tool in test_questions:
        # RAG evaluation
        start = time.time()
        server_tools_rag = rag.retrieve_hybrid(question)
        rag_time += time.time() - start

        if server_tools_rag is None:
            from tools_rag.tools import tools

            rag_ranked = tools
        else:
            rag_ranked = [tool for tools_list in server_tools_rag.values() for tool in tools_list]

        rag_names = [t["name"] for t in rag_ranked]
        rag_rank = _calculate_rank(expected_tool, rag_names)

        rag_results.append(
            EvaluationResult(
                question=question,
                expected=expected_tool,
                retrieved_names=rag_names,
                rank=rag_rank,
            )
        )

        # Skills evaluation
        start = time.time()
        server_tools_skills = skills.retrieve_skills(question, k=config.top_k)
        skills_time += time.time() - start

        # Calculate cost based on actual model
        query_cost = _calculate_query_cost(skills.model)
        skills_cost += query_cost

        if server_tools_skills is None:
            from tools_rag.tools import tools

            skills_ranked = tools
        else:
            skills_ranked = [
                tool for tools_list in server_tools_skills.values() for tool in tools_list
            ]

        skills_names = [t["name"] for t in skills_ranked]
        skills_rank = _calculate_rank(expected_tool, skills_names)

        skills_results.append(
            EvaluationResult(
                question=question,
                expected=expected_tool,
                retrieved_names=skills_names,
                rank=skills_rank,
            )
        )

    # Calculate metrics (only positive cases)
    rag_positive = [r for r in rag_results if not r.is_negative]
    skills_positive = [r for r in skills_results if not r.is_negative]

    rag_hits = sum(1 for r in rag_positive if r.is_hit)
    skills_hits = sum(1 for r in skills_positive if r.is_hit)

    rag_valid_ranks = [r.rank for r in rag_positive if r.is_hit]
    skills_valid_ranks = [r.rank for r in skills_positive if r.is_hit]

    rag_avg_rank = sum(rag_valid_ranks) / len(rag_valid_ranks) if rag_valid_ranks else 0
    skills_avg_rank = (
        sum(skills_valid_ranks) / len(skills_valid_ranks) if skills_valid_ranks else 0
    )

    # Print comparison table
    print("┌────────────────────────┬──────────────┬──────────────┐")
    print("│ Metric                 │ Hybrid RAG   │ LLM Skills   │")
    print("├────────────────────────┼──────────────┼──────────────┤")
    print(
        f"│ Hit Rate (Top-{config.top_k})        │ {rag_hits}/{len(rag_positive)} = {rag_hits/len(rag_positive):.1%}  │ {skills_hits}/{len(skills_positive)} = {skills_hits/len(skills_positive):.1%}  │"
    )
    print(
        f"│ Avg Rank (when found)  │ {rag_avg_rank:>12.2f} │ {skills_avg_rank:>12.2f} │"
    )
    print(
        f"│ Total Latency          │ {rag_time:>11.2f}s │ {skills_time:>11.2f}s │"
    )
    print(
        f"│ Avg Latency/Query      │ {rag_time/len(test_questions)*1000:>10.0f}ms │ {skills_time/len(test_questions)*1000:>10.0f}ms │"
    )
    print(f"│ Total Cost             │ {'$0.00':>12} │ ${skills_cost:>11.4f} │")
    print("└────────────────────────┴──────────────┴──────────────┘")

    # Show differences
    print(f"\n{'#':<4} {'Question':<50} {'RAG':<5} {'Skills':<5}")
    print("=" * 100)

    for i, (rag_r, skills_r) in enumerate(zip(rag_results, skills_results), 1):
        if rag_r.is_negative:
            continue  # Skip negative cases

        rag_symbol = "✓" if rag_r.is_hit else "✗"
        skills_symbol = "✓" if skills_r.is_hit else "✗"

        # Only show rows where results differ
        if rag_r.is_hit != skills_r.is_hit:
            print(
                f"{i:<4} {rag_r.question[:50]:<50} {rag_symbol:<5} {skills_symbol:<5}"
            )

    print("\n" + "=" * 100)
    print(
        f"Agreement: {sum(1 for r1, r2 in zip(rag_positive, skills_positive) if r1.is_hit == r2.is_hit)}/{len(rag_positive)} cases"
    )
    print("=" * 100)
