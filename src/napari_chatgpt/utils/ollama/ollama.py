"""Wrapper for the Ollama models."""

from concurrent.futures import ThreadPoolExecutor
from typing import List, Optional, Any

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.schema import LLMResult
from langchain_community.llms import Ollama

_aysync_ollama_thread_pool = ThreadPoolExecutor()


class OllamaFixed(Ollama):

    def _generate(
        self,
        prompts: List[str],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> LLMResult:
        """Run the LLM on the given prompt and input."""
        result = super()._generate(
            prompts,
            stop,
            None,
            run_manager,
            **kwargs
        )
        return result

    # async def _acall(
    #         self,
    #         prompt: str,
    #         stop: Optional[List[str]] = None,
    #         images: Optional[List[str]] = None,
    #         run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
    # ) -> str:
    #     """Run the LLM on the given prompt and input."""
    #     result = await asyncio.get_running_loop().run_in_executor(
    #         _aysync_ollama_thread_pool,
    #         self._call,
    #         prompt,
    #         stop,
    #         images, # images
    #         run_manager
    #     )
    #     return result

    # async def _agenerate(
    #     self,
    #     prompts: List[str],
    #     stop: Optional[List[str]] = None,
    #     run_manager: Optional[CallbackManagerForLLMRun] = None,
    #     **kwargs: Any,
    # ) -> LLMResult:
    #     result = await asyncio.get_running_loop().run_in_executor(
    #         _aysync_ollama_thread_pool,
    #         self._generate,
    #         prompts,
    #         stop,
    #         run_manager,
    #         **kwargs
    #     )
    #     return result
    #
