"""Wrapper for the GPT4All model."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional

from langchain.callbacks.manager import AsyncCallbackManagerForLLMRun
from langchain.llms import GPT4All

_aysync_gpt4all_thread_pool = ThreadPoolExecutor()


class GPT4AllFixed(GPT4All):

    async def _acall(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
    ) -> str:
        """Run the LLM on the given prompt and input."""
        result = await asyncio.get_running_loop().run_in_executor(
            _aysync_gpt4all_thread_pool,
            self._call,
            prompt,
            stop,
            run_manager
        )
        return result
