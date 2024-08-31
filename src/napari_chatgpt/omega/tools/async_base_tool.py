import asyncio
from concurrent.futures import ThreadPoolExecutor

from arbol import aprint
from langchain.tools import BaseTool

from napari_chatgpt.utils.notebook.jupyter_notebook import JupyterNotebookFile

_aysync_tool_thread_pool = ThreadPoolExecutor()


class AsyncBaseTool(BaseTool):
    _executor = ThreadPoolExecutor()

    notebook: JupyterNotebookFile = None

    def normalise_to_string(self, kwargs):

        # extract the value for args key in kwargs:
        query = kwargs.get('args', '') if isinstance(kwargs, dict) else kwargs

        # If query is a singleton list, extract the value:
        if isinstance(query, list) and len(query) == 1:
            query = query[0]

        # convert the query to string:
        query = str(query)
        return query
