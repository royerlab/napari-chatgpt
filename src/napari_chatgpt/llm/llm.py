from typing import Optional, List

from litemind.agent.messages.message import Message
from litemind.apis.base_api import BaseApi


class LLM:
    """
    A class to represent a simple completion LLM based on  Litemind.
    """

    def __init__(
        self, api: BaseApi, model_name: Optional[str] = None, temperature: float = 0.0
    ):
        """
        Initializes the LLM with the given API and model name.

        Parameters
        ----------
        api: BaseApi
            The API to use for generating text.
        model_name: Optional[str]
            The name of the model to use for text generation. If None, the default model will be used.
        temperature: float
            The temperature for the text generation. Default is 0.0, which means deterministic output.
        """
        self._api = api
        self.model_name = model_name
        self.temperature = temperature

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        variables: Optional[dict[str, str]] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
    ) -> List[Message]:
        """
        Generates a response from the LLM based on the provided prompt and instructions.
        Parameters
        ----------
        prompt: str
            The prompt to send to the LLM.
        system: Optional[str]
            Instructions to provide context or guidance for the LLM.
        variables: Optional[dict]
            Variables to format the prompt with.
        model_name: Optional[str]
            The name of the model to use for text generation. If None, the model set during initialization will be used.
        temperature: Optional[float]
            The temperature for the text generation. Default is None in which case it uses the temperature set during initialization.
        Returns
        -------
        List[Message]
            A list of messages containing the generated response from the LLM.
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

        # Append the user message to the messages list:
        messages.append(message)

        # Generate the response:
        response = self._api.generate_text(
            model_name=model_name, messages=messages, temperature=temperature
        )

        return response
