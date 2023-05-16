from arbol import aprint

from napari_chatgpt.utils.omega_plugins.discover_omega_plugins import \
    discover_omega_tools


def test_discover_omega_tools():
    tool_classes = discover_omega_tools()

    aprint(tool_classes)

    assert len(tool_classes) > 0
