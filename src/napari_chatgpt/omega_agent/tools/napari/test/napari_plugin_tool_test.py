"""Tests for napari_plugin_tool.py."""

import pytest


def test_plugin_catalog_init():
    """Catalog builds without raising."""
    from napari_chatgpt.omega_agent.tools.napari.napari_plugin_tool import (
        PluginCatalog,
    )

    catalog = PluginCatalog()
    assert catalog is not None
    assert isinstance(catalog.widgets, list)
    assert isinstance(catalog.readers, list)
    assert isinstance(catalog.writers, list)
    assert isinstance(catalog.error_log, list)


def test_plugin_catalog_skips_self():
    """napari-chatgpt should never appear in the catalog."""
    from napari_chatgpt.omega_agent.tools.napari.napari_plugin_tool import (
        PluginCatalog,
    )

    catalog = PluginCatalog()
    all_plugins = set()
    for w in catalog.widgets:
        all_plugins.add(w["plugin"])
    for r in catalog.readers:
        all_plugins.add(r["plugin"])
    for wr in catalog.writers:
        all_plugins.add(wr["plugin"])
    assert "napari-chatgpt" not in all_plugins


def test_plugin_catalog_format_for_prompt():
    """format_for_prompt returns a string (possibly empty-catalog marker)."""
    from napari_chatgpt.omega_agent.tools.napari.napari_plugin_tool import (
        PluginCatalog,
    )

    catalog = PluginCatalog()
    result = catalog.format_for_prompt()
    assert isinstance(result, str)
    assert len(result) > 0


def test_plugin_catalog_format_for_info():
    """format_for_info_query returns a string."""
    from napari_chatgpt.omega_agent.tools.napari.napari_plugin_tool import (
        PluginCatalog,
    )

    catalog = PluginCatalog()
    result = catalog.format_for_info_query()
    assert isinstance(result, str)
    assert len(result) > 0


def test_plugin_catalog_handles_empty():
    """An empty catalog formats safely without errors."""
    from napari_chatgpt.omega_agent.tools.napari.napari_plugin_tool import (
        PluginCatalog,
    )

    catalog = PluginCatalog()
    # Force empty state:
    catalog.widgets = []
    catalog.readers = []
    catalog.writers = []
    catalog._plugin_names = set()

    assert catalog.is_empty()
    assert catalog.get_plugin_count() == 0

    prompt_text = catalog.format_for_prompt()
    assert "(no plugins detected)" in prompt_text

    info_text = catalog.format_for_info_query()
    assert "No napari plugins detected" in info_text


def test_plugin_catalog_error_logging():
    """Import failures are logged, not raised."""
    from napari_chatgpt.omega_agent.tools.napari.napari_plugin_tool import (
        PluginCatalog,
    )

    # The catalog itself should not raise even if npe2 encounters issues:
    catalog = PluginCatalog()
    # error_log is a list; entries may or may not be present depending
    # on the environment, but it must always be a list:
    assert isinstance(catalog.error_log, list)


def test_plugin_catalog_signature_extraction():
    """If widgets exist, their signatures contain parentheses."""
    from napari_chatgpt.omega_agent.tools.napari.napari_plugin_tool import (
        PluginCatalog,
    )

    catalog = PluginCatalog()
    for w in catalog.widgets:
        sig = w.get("signature", "")
        if sig:
            assert "(" in sig and ")" in sig, (
                f"Widget '{w['display_name']}' has " f"malformed signature: {sig}"
            )


def test_napari_plugin_tool_init():
    """NapariPluginTool initializes with proper name and description."""
    from unittest.mock import MagicMock

    from napari_chatgpt.omega_agent.tools.napari.napari_plugin_tool import (
        NapariPluginTool,
    )

    tool = NapariPluginTool(
        llm=MagicMock(),
        to_napari_queue=MagicMock(),
        from_napari_queue=MagicMock(),
    )
    assert tool.name == "NapariPluginTool"
    assert isinstance(tool.description, str)
    assert len(tool.description) > 0
    assert tool.catalog is not None


def test_napari_plugin_tool_description_has_counts():
    """If plugins exist, the description includes counts."""
    from unittest.mock import MagicMock

    from napari_chatgpt.omega_agent.tools.napari.napari_plugin_tool import (
        NapariPluginTool,
    )

    tool = NapariPluginTool(
        llm=MagicMock(),
        to_napari_queue=MagicMock(),
        from_napari_queue=MagicMock(),
    )
    if not tool.catalog.is_empty():
        assert "plugin" in tool.description.lower()
        assert "widget" in tool.description.lower()
        assert "reader" in tool.description.lower()
        assert "writer" in tool.description.lower()


def test_napari_plugin_tool_info_mode():
    """Info keywords trigger catalog return, not sub-LLM."""
    from unittest.mock import MagicMock

    from napari_chatgpt.omega_agent.tools.napari.napari_plugin_tool import (
        NapariPluginTool,
    )

    tool = NapariPluginTool(
        llm=MagicMock(),
        to_napari_queue=MagicMock(),
        from_napari_queue=MagicMock(),
    )
    result = tool.run_omega_tool("list available plugins")
    assert isinstance(result, str)
    assert len(result) > 0
    # The LLM should NOT have been called:
    tool.llm.generate.assert_not_called()


def test_napari_plugin_tool_empty_catalog_fallback():
    """With empty catalog, execution mode returns helpful message."""
    from unittest.mock import MagicMock

    from napari_chatgpt.omega_agent.tools.napari.napari_plugin_tool import (
        NapariPluginTool,
    )

    tool = NapariPluginTool(
        llm=MagicMock(),
        to_napari_queue=MagicMock(),
        from_napari_queue=MagicMock(),
    )
    # Force empty catalog:
    tool.catalog.widgets = []
    tool.catalog.readers = []
    tool.catalog.writers = []
    tool.catalog._plugin_names = set()
    tool.prompt = None

    result = tool.run_omega_tool("denoise this image")
    assert "no" in result.lower() or "No" in result
    assert "plugin" in result.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
