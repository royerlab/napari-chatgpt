from functools import lru_cache
from typing import List, Optional

from litemind.apis.model_features import ModelFeatures

from napari_chatgpt.llm.api_keys.api_key import set_api_key
from napari_chatgpt.llm.llm import LLM

__litemind_api = None


def is_llm_available() -> bool:
    """
    Determine if any non-default LiteMind API implementations are available and initialized.
    
    Returns:
        bool: True if at least one LiteMind API implementation (other than DefaultApi and CombinedApi) exists and the global API instance is initialized; otherwise, False.
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
    Return the global LiteMind API instance, initializing it if necessary.
    
    Returns:
        CombinedApi: The singleton LiteMind API instance for interacting with multiple LLM providers.
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
    Retrieve the list of model names that support text generation from the LiteMind API.
    
    Returns:
        List[str]: Names of available models with text generation capability.
    """
    api = get_litemind_api()
    from litemind.apis.model_features import ModelFeatures

    return api.list_models(features=[ModelFeatures.TextGeneration])


def has_model_support_for(model_name: str, features: List[ModelFeatures]) -> bool:
    """
    Determine whether the specified model supports all provided features.
    
    Parameters:
        model_name (str): Name of the model to check.
        features (List[ModelFeatures]): Features to verify support for.
    
    Returns:
        bool: True if the model supports every feature in the list; otherwise, False.
    """
    api = get_litemind_api()
    return api.has_model_support_for(features=features, model_name=model_name)


def get_llm(
    model_name: Optional[str] = None,
    temperature: float = 0.0,
    features: Optional[List[ModelFeatures]] = None,
) -> LLM:
    """
    Return an LLM instance configured with the specified model, temperature, and required features.
    
    If no model name is provided, selects the best available model supporting the requested features (defaulting to text generation if none are specified).
    
    Parameters:
        model_name (str, optional): Name of the model to use. If None, the best model for the features is selected.
        temperature (float): Sampling temperature for the LLM; 0.0 produces deterministic output.
        features (List[ModelFeatures], optional): List of required features the model must support.
    
    Returns:
        LLM: An LLM instance configured with the chosen model and temperature.
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
