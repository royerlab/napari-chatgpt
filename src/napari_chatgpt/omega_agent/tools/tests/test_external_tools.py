"""Tests for entry-point-based tool extensibility."""

from unittest.mock import MagicMock, patch

from napari_chatgpt.omega_agent.omega_init import _discover_external_tools
from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool


class _MockValidTool(BaseOmegaTool):
    """A valid external tool for testing."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "MockValidTool"
        self.description = "A mock tool for testing"

    def run_omega_tool(self, query: str = ""):
        return "mock result"


class _NotATool:
    """Not a subclass of BaseOmegaTool."""

    pass


class TestDiscoverExternalTools:
    """Tests for _discover_external_tools."""

    def test_valid_tool_registered(self):
        tools = []
        tool_context = {}

        ep = MagicMock()
        ep.name = "mock_tool"
        ep.load.return_value = _MockValidTool

        with patch("importlib.metadata.entry_points", return_value=[ep]):
            _discover_external_tools(tool_context, tools)

        assert len(tools) == 1
        assert isinstance(tools[0], _MockValidTool)

    def test_non_subclass_rejected(self):
        tools = []
        tool_context = {}

        ep = MagicMock()
        ep.name = "bad_tool"
        ep.load.return_value = _NotATool

        with patch("importlib.metadata.entry_points", return_value=[ep]):
            _discover_external_tools(tool_context, tools)

        assert len(tools) == 0

    def test_non_class_rejected(self):
        tools = []
        tool_context = {}

        ep = MagicMock()
        ep.name = "function_tool"
        ep.load.return_value = lambda: "not a class"

        with patch("importlib.metadata.entry_points", return_value=[ep]):
            _discover_external_tools(tool_context, tools)

        assert len(tools) == 0

    def test_load_error_handled(self):
        tools = []
        tool_context = {}

        ep = MagicMock()
        ep.name = "broken_tool"
        ep.load.side_effect = ImportError("module not found")

        with patch("importlib.metadata.entry_points", return_value=[ep]):
            _discover_external_tools(tool_context, tools)

        assert len(tools) == 0

    def test_no_entry_points(self):
        tools = []
        tool_context = {}

        with patch("importlib.metadata.entry_points", return_value=[]):
            _discover_external_tools(tool_context, tools)

        assert len(tools) == 0
