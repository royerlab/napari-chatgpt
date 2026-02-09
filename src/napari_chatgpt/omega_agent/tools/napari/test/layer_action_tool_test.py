"""Tests for layer_action_tool.py."""

import pytest

# ------------------------------------------------------------------
# Metadata parsing tests
# ------------------------------------------------------------------


def test_parse_action_metadata_full():
    """All four metadata fields are extracted correctly."""
    from napari_chatgpt.omega_agent.tools.napari.layer_action_tool import (
        _parse_action_metadata,
    )

    code = (
        "# ACTION_TITLE: Invert Image\n"
        "# ACTION_CATEGORY: filter\n"
        "# ACTION_LAYER_TYPE: image\n"
        "# ACTION_KEYBINDING: Ctrl+Shift+I\n"
        "\n"
        "def invert_image(ll):\n"
        "    pass\n"
    )
    meta = _parse_action_metadata(code)
    assert meta["title"] == "Invert Image"
    assert meta["category"] == "filter"
    assert meta["layer_type"] == "image"
    assert meta["keybinding"] == "Ctrl+Shift+I"


def test_parse_action_metadata_defaults():
    """Missing optional fields get default values."""
    from napari_chatgpt.omega_agent.tools.napari.layer_action_tool import (
        _parse_action_metadata,
    )

    code = (
        "# ACTION_TITLE: My Action\n"
        "\n"
        "def my_action(ll):\n"
        "    pass\n"
    )
    meta = _parse_action_metadata(code)
    assert meta["title"] == "My Action"
    assert meta["category"] == "filter"  # default
    assert meta["layer_type"] == "any"  # default
    assert meta["keybinding"] is None  # default


def test_parse_action_metadata_no_metadata():
    """Code with no metadata comments gets all defaults."""
    from napari_chatgpt.omega_agent.tools.napari.layer_action_tool import (
        _parse_action_metadata,
    )

    code = "def my_action(ll):\n    pass\n"
    meta = _parse_action_metadata(code)
    assert meta["title"] == "Omega Action"
    assert meta["category"] == "filter"
    assert meta["layer_type"] == "any"
    assert meta["keybinding"] is None


def test_parse_action_metadata_case_insensitive_category():
    """Category value is lowercased."""
    from napari_chatgpt.omega_agent.tools.napari.layer_action_tool import (
        _parse_action_metadata,
    )

    code = "# ACTION_TITLE: Test\n# ACTION_CATEGORY: Segment\n"
    meta = _parse_action_metadata(code)
    assert meta["category"] == "segment"


def test_parse_action_metadata_extra_spaces():
    """Extra whitespace in metadata values is stripped."""
    from napari_chatgpt.omega_agent.tools.napari.layer_action_tool import (
        _parse_action_metadata,
    )

    code = "#   ACTION_TITLE:   Normalize Image   \n"
    meta = _parse_action_metadata(code)
    assert meta["title"] == "Normalize Image"


# ------------------------------------------------------------------
# Metadata stripping tests
# ------------------------------------------------------------------


def test_strip_metadata_comments():
    """ACTION_* lines are removed from code."""
    from napari_chatgpt.omega_agent.tools.napari.layer_action_tool import (
        _strip_metadata_comments,
    )

    code = (
        "# ACTION_TITLE: Invert Image\n"
        "# ACTION_CATEGORY: filter\n"
        "import numpy as np\n"
        "\n"
        "def invert_image(ll):\n"
        "    pass\n"
    )
    result = _strip_metadata_comments(code)
    assert "ACTION_TITLE" not in result
    assert "ACTION_CATEGORY" not in result
    assert "import numpy as np" in result
    assert "def invert_image(ll):" in result


# ------------------------------------------------------------------
# Tool initialization tests
# ------------------------------------------------------------------


def test_layer_action_tool_init():
    """Tool initializes with proper name and description."""
    from unittest.mock import MagicMock

    from napari_chatgpt.omega_agent.tools.napari.layer_action_tool import (
        NapariLayerActionTool,
    )

    tool = NapariLayerActionTool(
        llm=MagicMock(),
        to_napari_queue=MagicMock(),
        from_napari_queue=MagicMock(),
    )
    assert tool.name == "NapariLayerActionTool"
    assert isinstance(tool.description, str)
    assert "context menu" in tool.description.lower()
    assert "layer action" in tool.description.lower()


def test_layer_action_tool_has_prompt():
    """Tool has a valid prompt template."""
    from unittest.mock import MagicMock

    from napari_chatgpt.omega_agent.tools.napari.layer_action_tool import (
        NapariLayerActionTool,
    )

    tool = NapariLayerActionTool(
        llm=MagicMock(),
        to_napari_queue=MagicMock(),
        from_napari_queue=MagicMock(),
    )
    assert tool.prompt is not None
    assert "{input}" in tool.prompt
    assert "{instructions}" in tool.prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
