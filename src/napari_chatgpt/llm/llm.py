"""Lightweight LLM wrapper for text generation via the LiteMind API."""

from litemind.agent.messages.message import Message
from litemind.apis.base_api import BaseApi


class LLM:
    """Simple text-completion wrapper around a LiteMind ``BaseApi``.

    Provides a ``generate`` method that accepts a prompt string (with
    optional system instructions and template variables) and returns a
    list of ``Message`` objects from the underlying LLM provider.
    """

    def __init__(
        self, api: BaseApi, model_name: str | None = None, temperature: float = 0.0
    ):
        """Initialize the LLM wrapper.

        Args:
            api: LiteMind API backend used for text generation.
            model_name: Model to use. If ``None``, the API's default
                model is used.
            temperature: Sampling temperature (0.0 = deterministic).
        """
        self._api = api
        self.model_name = model_name
        self.temperature = temperature

    def generate(
        self,
        prompt: str,
        system: str | None = None,
        variables: dict[str, str] | None = None,
        model_name: str | None = None,
        temperature: float | None = None,
    ) -> list[Message]:
        """Generate a response from the LLM.

        Args:
            prompt: User prompt (may contain template placeholders when
                *variables* is provided).
            system: Optional system-level instructions prepended to the
                conversation.
            variables: Template variables substituted into *prompt*.
            model_name: Override the model set at init time.
            temperature: Override the temperature set at init time.

        Returns:
            A list of ``Message`` objects containing the LLM's response.
        """

        # List of messages to send to the LLM:
        messages = []

        # If instructions are provided, append them as a system message:
        if system:
            messages.append(Message(role="system", text=system))

        # If variables are provided, attempt to format the prompt with them:
        if variables:
            message = Message(role="user")
            message.append_templated_text(template=prompt, **variables)
        else:
            message = Message(role="user", text=prompt)

        if temperature is None:
            temperature = self.temperature

        if model_name is None:
            model_name = self.model_name

        # Append the user message to the messages list:
        messages.append(message)

        # Generate the response:
        response = self._api.generate_text(
            model_name=model_name, messages=messages, temperature=temperature
        )

        return response
