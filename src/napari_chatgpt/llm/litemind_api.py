from functools import lru_cache
from typing import List, Optional

from litemind.apis.model_features import ModelFeatures

from napari_chatgpt.llm.api_keys.api_key import set_api_key
from napari_chatgpt.llm.llm import LLM

__litemind_api = None


def is_available() -> bool:
    """
    Checks if the LiteMind API is available.

    This function checks if the global LiteMind API instance is initialized.
    If it is not initialized, it will return False, indicating that the API
    is not available.

    Returns:
        bool: True if the LiteMind API is available, False otherwise.
    """

    # Check that the list API_IMPLEMENTATIONS contains at least one API implementation except for DefaultApi and CombinedApi:
    from litemind import API_IMPLEMENTATIONS

    api_implementations = list(API_IMPLEMENTATIONS)

    # Remove DefaultApi and CombinedApi from the list:
    from litemind.apis.default_api import DefaultApi
    from litemind.apis.combined_api import CombinedApi

    api_implementations = [
        api for api in api_implementations if api not in (DefaultApi, CombinedApi)
    ]

    # If there are no API implementations available, return False:
    if len(api_implementations) == 0:
        return False

    # If the global LiteMind API instance is initialized, return True:
    if get_litemind_api() is not None:
        return True

    # Otherwise, return False:
    return False


def get_litemind_api() -> "CombinedApi":
    """
    Returns the global LiteMind API instance.

    This function provides access to the global LiteMind API instance,
    which is initialized with the CombinedApi class. It allows for
    interaction with various LLM providers and features.

    Returns:
        CombinedApi: The global LiteMind API instance.
    """

    # This module provides a global instance of the LiteMind API.
    global __litemind_api

    # If the global instance is not initialized, create it.
    if __litemind_api is None:
        set_api_key("OpenAI")
        set_api_key("Anthropic")
        set_api_key("Gemini")

        from litemind.apis.combined_api import CombinedApi

        __litemind_api = CombinedApi()

    return __litemind_api


@lru_cache
def get_model_list() -> List[str]:
    """
    Returns a list of available models from the LiteMind API.

    This function retrieves the list of models supported by the global
    LiteMind API instance.

    Returns:
        list: A list of model names available in the LiteMind API.
    """
    api = get_litemind_api()
    from litemind.apis.model_features import ModelFeatures

    return api.list_models(features=[ModelFeatures.TextGeneration])


def get_llm(
    model_name: Optional[str] = None,
    temperature: float = 0.0,
    features: Optional[List[ModelFeatures]] = None,
) -> LLM:
    """
    Returns an LLM instance based on the provided features.

    Parameters
    ----------
    model_name: str
        The name of the model to use. If None, the best model for the
        specified features will be selected.
    temperature: float
        The temperature for the LLM. Default is 0.0, which means deterministic output.
    features : List[ModelFeatures]
        A list of features that the desired model should support.
        This is used to determine the best model for the given features.

    Returns
    -------
    LLM: An instance of the LLM class configured with the best model
         for the specified features.

    """

    if features is None:
        # Default to text generation if no features are specified:
        features = [ModelFeatures.TextGeneration]

    # Get API:
    api = get_litemind_api()

    # If model_name is None, get the best model for the specified features:
    model_name = api.get_best_model(features) if model_name is None else model_name

    # Instantiate LLM:
    llm: LLM = LLM(api=api, model_name=model_name, temperature=temperature)

    return llm
