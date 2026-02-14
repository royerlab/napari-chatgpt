"""Tests for BaseOmegaTool.normalise_to_string() and pretty_string()."""

from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool


class ConcreteOmegaTool(BaseOmegaTool):
    """A concrete test tool for testing."""

    def run_omega_tool(self, query: str = ""):
        return f"ran: {query}"


def _make_tool(**kwargs):
    return ConcreteOmegaTool(
        name=kwargs.get("name", "TestTool"),
        description=kwargs.get("description", "A test tool for unit tests."),
    )


class TestNormaliseToString:
    def test_dict_with_args_key(self):
        tool = _make_tool()
        assert tool.normalise_to_string({"args": "hello"}) == "hello"

    def test_dict_with_empty_args(self):
        tool = _make_tool()
        assert tool.normalise_to_string({"args": ""}) == ""

    def test_dict_singleton_list_unwrap(self):
        tool = _make_tool()
        assert tool.normalise_to_string({"args": ["single"]}) == "single"

    def test_dict_non_singleton_list(self):
        tool = _make_tool()
        result = tool.normalise_to_string({"args": ["a", "b"]})
        assert result == "['a', 'b']"

    def test_plain_string(self):
        tool = _make_tool()
        assert tool.normalise_to_string("plain string") == "plain string"

    def test_dict_no_args_key(self):
        tool = _make_tool()
        assert tool.normalise_to_string({"other_key": "val"}) == ""


class TestPrettyString:
    def test_short_description(self):
        tool = _make_tool(description="A short description.")
        result = tool.pretty_string()
        assert result == "TestTool: A short description."

    def test_long_description_truncated(self):
        desc = "A" * 80 + ". This part should be truncated. And this too."
        tool = _make_tool(description=desc)
        result = tool.pretty_string()
        assert "[...]" in result
        assert result.startswith("TestTool: ")

    def test_long_description_no_period(self):
        desc = "A" * 100
        tool = _make_tool(description=desc)
        result = tool.pretty_string()
        # When no period found after char 80, find returns -1
        # so description[:0] + "[...]" = "[...]"
        assert result.startswith("TestTool: ")
