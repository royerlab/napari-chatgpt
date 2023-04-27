from langchain import LLMMathChain
from langchain.schema import BaseLanguageModel

from napari_chatgpt.omega.tools.async_base_tool import AsyncBaseTool


class MathTool(AsyncBaseTool):
    """Tool that can do math"""

    llm: BaseLanguageModel
    name = "Calculator"
    description = (
        "Useful for when you need to answer questions about math."
    )

    def _run(self, query: str) -> str:
        """Use the Wikipedia tool."""
        return LLMMathChain(llm=self.llm).run()

    async def _arun(self, query: str) -> str:
        return await LLMMathChain(llm=self.llm).arun()
