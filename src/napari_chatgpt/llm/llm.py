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
        Initialize an LLM instance with the specified API, model name, and temperature.
        
        Parameters:
            model_name (Optional[str]): Name of the language model to use, or None for the default.
            temperature (float): Controls randomness in text generation; 0.0 produces deterministic output.
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
        Generate a list of messages in response to a prompt using the language model.
        
        Parameters:
            prompt (str): The input prompt for the language model.
            system (Optional[str]): Optional system-level instructions or context.
            variables (Optional[dict[str, str]]): Optional variables to format the prompt template.
            model_name (Optional[str]): Optional override for the model name.
            temperature (Optional[float]): Optional override for generation randomness.
        
        Returns:
            List[Message]: The generated response as a list of Message objects.
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
