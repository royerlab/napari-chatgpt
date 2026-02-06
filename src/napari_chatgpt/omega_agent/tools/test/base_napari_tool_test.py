"""Tests for BaseNapariTool._prepare_code() and _get_delegated_code()."""

from queue import Queue
from unittest.mock import MagicMock

import pytest

from napari_chatgpt.omega_agent.tools.base_napari_tool import (
    BaseNapariTool,
    _get_delegated_code,
)


class ConcreteNapariTool(BaseNapariTool):
    """A concrete subclass of BaseNapariTool for testing."""

    def _run_code(self, query, code, viewer):
        return f"Success: executed"


def _make_tool(**kwargs):
    """Create a ConcreteNapariTool with sensible defaults and no LLM."""
    mock_llm = MagicMock()
    mock_message = MagicMock()
    mock_message.to_plain_text.return_value = "mock code"
    mock_llm.generate.return_value = [mock_message]

    return ConcreteNapariTool(
        name=kwargs.get("name", "TestTool"),
        description=kwargs.get("description", "A test tool."),
        code_prefix=kwargs.get("code_prefix", ""),
        prompt=kwargs.get("prompt", None),
        to_napari_queue=kwargs.get("to_napari_queue", Queue()),
        from_napari_queue=kwargs.get("from_napari_queue", Queue()),
        llm=kwargs.get("llm", mock_llm),
        fix_imports=kwargs.get("fix_imports", False),
        install_missing_packages=kwargs.get("install_missing_packages", False),
        fix_bad_calls=kwargs.get("fix_bad_calls", False),
    )


class TestPrepareCode:
    def test_extracts_code_from_markdown(self):
        tool = _make_tool()
        code = tool._prepare_code(
            "```python\nprint('hello')\n```",
            markdown=True,
            do_fix_imports=False,
            do_fix_bad_calls=False,
            do_install_missing_packages=False,
        )
        assert "print('hello')" in code

    def test_code_prefix_prepended(self):
        tool = _make_tool(code_prefix="import os\n")
        code = tool._prepare_code(
            "x = 1",
            markdown=False,
            do_fix_imports=False,
            do_fix_bad_calls=False,
            do_install_missing_packages=False,
        )
        assert "import os" in code
        assert "x = 1" in code

    def test_filters_napari_viewer_creation(self):
        tool = _make_tool()
        code = tool._prepare_code(
            "viewer = napari.Viewer()\nx = 1",
            markdown=False,
            do_fix_imports=False,
            do_fix_bad_calls=False,
            do_install_missing_packages=False,
        )
        assert "napari.Viewer(" not in code
        assert "x = 1" in code

    def test_filters_dock_widget(self):
        tool = _make_tool()
        code = tool._prepare_code(
            "viewer.window.add_dock_widget(my_widget)\nx = 1",
            markdown=False,
            do_fix_imports=False,
            do_fix_bad_calls=False,
            do_install_missing_packages=False,
        )
        assert "add_dock_widget" not in code
        assert "x = 1" in code


class TestGetDelegatedCode:
    def test_get_cellpose_code(self):
        code = _get_delegated_code("cellpose", signature=False)
        assert len(code) > 0
        assert isinstance(code, str)

    def test_get_cellpose_signature(self):
        code = _get_delegated_code("cellpose", signature=True)
        assert len(code) > 0
        # Signature should be a subset of full code
        full_code = _get_delegated_code("cellpose", signature=False)
        assert len(code) < len(full_code)

    def test_get_classic_code(self):
        code = _get_delegated_code("classic", signature=False)
        assert len(code) > 0

    def test_get_stardist_code(self):
        code = _get_delegated_code("stardist", signature=False)
        assert len(code) > 0

    def test_nonexistent_raises(self):
        with pytest.raises(FileNotFoundError):
            _get_delegated_code("nonexistent_algorithm", signature=False)
