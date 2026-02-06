import pytest
from duckduckgo_search.exceptions import DuckDuckGoSearchException

from napari_chatgpt.omega_agent.tools.search.wikipedia_search_tool import (
    WikipediaSearchTool,
)


def test_wikipedia_search_tool():
    try:
        tool = WikipediaSearchTool()
        query = "Albert Einstein"
        result = tool.run_omega_tool(query)

        # Skip if search returned no results (flaky external dependency)
        if not result or result.strip() == "":
            pytest.skip("Wikipedia/DuckDuckGo search returned no results")

        assert "Einstein" in result or "physicist" in result or "relativity" in result

    except DuckDuckGoSearchException as e:
        pytest.skip(f"DuckDuckGo search unavailable: {e}")
