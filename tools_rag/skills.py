"""LLM-based tool selection (Skills approach)."""

import json
import os
from typing import Optional
from openai import OpenAI


class ToolsSkills:
    """
    LLM-based tool selector that provides all tools to the LLM for selection.

    Unlike ToolsRAG which uses hybrid retrieval (semantic + BM25), this approach
    sends all available tools to an LLM and asks it to select the most relevant ones.
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: Optional[str] = None,
        temperature: float = 0.0,
    ):
        """
        Initialize the LLM-based tool selector.

        Args:
            model: OpenAI model to use (default: gpt-4o-mini for cost efficiency)
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            temperature: Sampling temperature (0 = deterministic)
        """
        self.model = model
        self.temperature = temperature
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.tools_by_name = {}  # {tool_name: tool_dict}

    def populate_tools(self, tools: list[dict]) -> None:
        """
        Populate the tool catalog (replaces existing tools).

        Args:
            tools: List of tool dictionaries with 'name', 'desc', 'params', 'server'
        """
        self.tools_by_name = {tool["name"]: tool.copy() for tool in tools}

    def add_tools(self, tools: list[dict]) -> None:
        """
        Add or update tools in the catalog (upsert behavior).

        Args:
            tools: List of tool dictionaries to add/update
        """
        for tool in tools:
            self.tools_by_name[tool["name"]] = tool.copy()

    def remove_tools(self, tool_names: list[str]) -> None:
        """
        Remove tools from the catalog.

        Args:
            tool_names: List of tool names to remove
        """
        for name in tool_names:
            self.tools_by_name.pop(name, None)

    def get_all_tools(self) -> list[dict]:
        """Get all tools in the catalog."""
        return list(self.tools_by_name.values())

    def retrieve_skills(
        self, query: str, k: int = 10, filter_tools: bool = True
    ) -> dict[str, list[dict]] | None:
        """
        Select top-k most relevant tools for the query using LLM.

        Args:
            query: User query to match tools against
            k: Number of tools to retrieve
            filter_tools: If False, returns None (caller should use all tools)

        Returns:
            Dictionary mapping server names to lists of tools (without 'server' key),
            or None if filter_tools=False
        """
        if not filter_tools:
            return None

        if not self.tools_by_name:
            return {}

        all_tools = self.get_all_tools()

        # If k >= total tools, no need to filter
        if k >= len(all_tools):
            return self._group_by_server(all_tools)

        # Build prompt with all tools
        tools_list = "\n".join(
            [
                f"{i+1}. {tool['name']}: {tool['desc']}"
                for i, tool in enumerate(all_tools)
            ]
        )

        prompt = f"""You are a tool selection expert. Given a user query, select the {k} most relevant tools from the available catalog.

User Query: "{query}"

Available Tools:
{tools_list}

Instructions:
- Select exactly {k} tools (or fewer if not enough are relevant)
- Return a JSON object with a "selected_tools" array containing tool names
- Be precise and only include truly relevant tools

Response format:
{{"selected_tools": ["tool_name_1", "tool_name_2", ...]}}"""

        try:
            # Call OpenAI API with JSON mode
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=self.temperature,
                max_tokens=500,
                response_format={"type": "json_object"},
            )

            # Parse response
            content = response.choices[0].message.content.strip()
            
            # Handle both direct array and wrapped object
            try:
                result = json.loads(content)
                # If it's a dict with "tools" or "selected_tools" key
                if isinstance(result, dict):
                    selected_names = result.get("selected_tools", result.get("tools", []))
                else:
                    selected_names = result
            except json.JSONDecodeError:
                # Try to extract JSON array from markdown code blocks
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                selected_names = json.loads(content)

            # Validate and get tool objects
            selected_tools = []
            for name in selected_names:
                if name in self.tools_by_name:
                    selected_tools.append(self.tools_by_name[name])

            return self._group_by_server(selected_tools)

        except (json.JSONDecodeError, KeyError, IndexError) as e:
            print(f"Error calling LLM for tool selection: {e}")
            # Fallback: return first k tools
            return self._group_by_server(all_tools[:k])

    def _group_by_server(self, tools: list[dict]) -> dict[str, list[dict]]:
        """
        Group tools by server, removing the 'server' key from each tool.

        Args:
            tools: List of tool dictionaries

        Returns:
            Dictionary mapping server names to lists of tools
        """
        server_tools = {}
        for tool in tools:
            tool_copy = tool.copy()
            server = tool_copy.pop("server", "default")

            if server not in server_tools:
                server_tools[server] = []
            server_tools[server].append(tool_copy)

        return server_tools
