import pytest
from duckduckgo_search.exceptions import DuckDuckGoSearchException

from napari_chatgpt.omega_agent.tools.search.web_search_tool import (
    WebSearchTool,
)


@pytest.mark.integration
def test_web_search_tool():
    try:
        tool = WebSearchTool()
        query = "What is zebrahub?"
        result = tool.run_omega_tool(query)

        # Skip if search returned no results (flaky external dependency)
        if not result or result.strip() == "":
            pytest.skip("Web search returned no results")

        assert "atlas" in result or "zebrafish" in result or "RNA" in result

    except DuckDuckGoSearchException as e:
        pytest.skip(f"DuckDuckGo search unavailable: {e}")
    except Exception as e:
        if "rate" in str(e).lower() or "timeout" in str(e).lower():
            pytest.skip(f"Web search failed due to network issue: {e}")
        raise
