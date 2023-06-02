"""Callback Handler that prints to std out."""

from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from arbol import aprint
from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import AgentAction, AgentFinish, LLMResult, BaseMessage


class ArbolCallbackHandler(BaseCallbackHandler):
    """Callback Handler that prints to std out."""

    def __init__(self, prefix: str = '', verbose: bool = False) -> None:
        """Initialize callback handler."""
        self.prefix = prefix
        self.verbose = verbose

    def on_chat_model_start(
            self,
            serialized: Dict[str, Any],
            messages: List[List[BaseMessage]],
            *,
            run_id: UUID,
            parent_run_id: Optional[UUID] = None,
            **kwargs: Any,
    ) -> Any:
        """Run when a chat model starts running."""
        if self.verbose:
            aprint(
                f"{self.prefix} on_chat_model_start: serialized={serialized},  messages={messages}, run_id={run_id}, parent_run_id={parent_run_id}, kwargs={kwargs}")

    def on_llm_start(
            self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Print out the prompts."""
        if self.verbose:
            aprint(
                f"{self.prefix} on_llm_start: serialized={serialized},  prompts={prompts}, kwargs={kwargs}")

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        if self.verbose:
            aprint(
                f"{self.prefix} on_llm_end: response={response}, kwargs={kwargs}")

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        pass
        # aprint(
        #     f"{self.prefix} on_llm_new_token: token={token}, kwargs={kwargs}")

    def on_llm_error(
            self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        if self.verbose:
            aprint(
                f"{self.prefix} on_llm_error: error={error}, kwargs={kwargs}")

    def on_chain_start(
            self, serialized: Dict[str, Any], inputs: Dict[str, Any],
            **kwargs: Any
    ) -> None:
        """Print out that we are entering a chain."""
        class_name = serialized["name"]
        if self.verbose:
            aprint(
                f"{self.prefix} on_chain_start: class_name={class_name}, kwargs={kwargs}")

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Print out that we finished a chain."""
        # print("\n\033[1m> Finished chain.\033[0m")
        if self.verbose:
            aprint(
                f"{self.prefix} on_chain_end: outputs={outputs}, kwargs={kwargs}")

    def on_chain_error(
            self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        """Do nothing."""
        if self.verbose:
            aprint(
                f"{self.prefix} on_chain_error: error={error}, kwargs={kwargs}")

    def on_tool_start(
            self,
            serialized: Dict[str, Any],
            input_str: str,
            **kwargs: Any,
    ) -> None:
        """Do nothing."""
        if self.verbose:
            aprint(
                f"{self.prefix} on_tool_start: input_str={input_str}, kwargs={kwargs}")

    def on_agent_action(
            self, action: AgentAction, color: Optional[str] = None,
            **kwargs: Any
    ) -> Any:
        """Run on agent action."""
        if self.verbose:
            aprint(
                f"{self.prefix} on_agent_action: action={action}, kwargs={kwargs}")

    def on_tool_end(
            self,
            output: str,
            color: Optional[str] = None,
            observation_prefix: Optional[str] = None,
            llm_prefix: Optional[str] = None,
            **kwargs: Any,
    ) -> None:
        if self.verbose:
            aprint(
                f"{self.prefix} on_agent_action: output={output}, observation_prefix={observation_prefix}, llm_prefix={llm_prefix}, kwargs={kwargs}")

    def on_tool_error(
            self, error: Union[Exception, KeyboardInterrupt], **kwargs: Any
    ) -> None:
        if self.verbose:
            aprint(
                f"{self.prefix} on_tool_error: error={error}, kwargs={kwargs}")

    def on_text(
            self,
            text: str,
            color: Optional[str] = None,
            end: str = "",
            **kwargs: Any,
    ) -> None:
        if self.verbose:
            aprint(
                f"{self.prefix} on_text: text={text}, end={end}, kwargs={kwargs}")

    def on_agent_finish(
            self, finish: AgentFinish, color: Optional[str] = None,
            **kwargs: Any
    ) -> None:
        if self.verbose:
            aprint(
                f"{self.prefix} on_agent_finish: finish={finish}, kwargs={kwargs}")
