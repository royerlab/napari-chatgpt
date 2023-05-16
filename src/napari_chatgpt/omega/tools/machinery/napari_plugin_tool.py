"""A tool for running python code in a REPL."""
from typing import Any

from napari import Viewer

from napari_chatgpt.omega.tools.machinery.napari_base_tool import NapariBaseTool


class NapariPluginTool(NapariBaseTool):
    plugin_tool_instance: Any

    def _run_code(self, **kwargs) -> str:
        return self.plugin_tool_instance.run(**kwargs)
