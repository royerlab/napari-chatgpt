import asyncio
from concurrent.futures import ThreadPoolExecutor

from arbol import aprint
from langchain.tools import BaseTool


_aysnc_tool_thread_pool = ThreadPoolExecutor()


class AsyncBaseTool(BaseTool):

    _executor = ThreadPoolExecutor()

    async def _arun(self, query: str) -> str:
        """Use the tool asynchronously."""
        aprint(f"Starting async call to {type(self).__name__}({query}) ")
        result = await asyncio.get_running_loop().run_in_executor(_aysnc_tool_thread_pool,
                                                                  self.run,
                                                                  self,
                                                                  query)
        return result

