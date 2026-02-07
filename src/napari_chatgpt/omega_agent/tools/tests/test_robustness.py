"""Tests for robustness fixes in omega tools."""

from unittest.mock import patch

from napari_chatgpt.omega_agent.tools.base_omega_tool import BaseOmegaTool


class _DummyTool(BaseOmegaTool):
    """A concrete subclass for testing BaseOmegaTool."""

    def run_omega_tool(self, query: str = ""):
        return "ok"


def test_pretty_string_no_period():
    """Fix 5: pretty_string handles missing period after pos 80."""
    tool = _DummyTool()
    # Description longer than 80 chars with no period after position 80
    tool.description = "A" * 100
    result = tool.pretty_string()
    assert len(result) > 0
    assert "..." in result
    assert "A" * 80 in result


def test_pretty_string_with_period():
    """pretty_string works normally when a period exists after pos 80."""
    tool = _DummyTool()
    tool.description = "A" * 85 + ". More text here."
    result = tool.pretty_string()
    assert result.endswith("[...]")
    assert "A" * 85 in result


def test_pretty_string_short_description():
    """pretty_string returns full description when shorter than 80 chars."""
    tool = _DummyTool()
    tool.description = "Short description"
    result = tool.pretty_string()
    assert "Short description" in result


def test_pip_install_tool_exception_before_split():
    """Fix 2: PipInstallTool except block handles packages var."""
    from napari_chatgpt.omega_agent.tools.special.pip_install_tool import (
        PipInstallTool,
    )

    tool = PipInstallTool()

    # Patch is_package_installed to raise, which happens after packages is
    # assigned but tests that the except block can reference `packages`.
    with patch(
        "napari_chatgpt.omega_agent.tools.special"
        ".pip_install_tool.is_package_installed",
        side_effect=RuntimeError("boom"),
    ):
        result = tool.run_omega_tool("pkg1,pkg2")
    assert "Error" in result
    # The except block should be able to reference `packages` without NameError
    assert "pkg1" in result or "boom" in result


def test_functions_info_tool_exception_handler():
    """Fix 3: PythonFunctionsInfoTool except block is safe."""
    from napari_chatgpt.omega_agent.tools.special.functions_info_tool import (
        PythonFunctionsInfoTool,
    )

    tool = PythonFunctionsInfoTool()
    with patch(
        "napari_chatgpt.omega_agent.tools.special"
        ".functions_info_tool.extract_package_path",
        side_effect=RuntimeError("test error"),
    ):
        result = tool.run_omega_tool("some.function.path")
    assert "Error" in result
    assert "test error" in result
    # Should not crash with NameError
