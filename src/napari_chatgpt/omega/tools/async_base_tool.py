import asyncio
from concurrent.futures import ThreadPoolExecutor

from arbol import aprint
from langchain.tools import BaseTool

from napari_chatgpt.utils.notebook.jupyter_notebook import JupyterNotebookFile

_aysync_tool_thread_pool = ThreadPoolExecutor()


class AsyncBaseTool(BaseTool):
    _executor = ThreadPoolExecutor()

    notebook: JupyterNotebookFile = None

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        aprint(f"Starting async call to {type(self).__name__}({query}) ")
        result = await asyncio.get_running_loop().run_in_executor(
            _aysync_tool_thread_pool,
            self._run,
            query)
        return result
