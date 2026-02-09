from __future__ import annotations

import os
from functools import lru_cache
from typing import TYPE_CHECKING

from arbol import aprint, asection
from litemind.apis.model_features import ModelFeatures

from napari_chatgpt.llm.api_keys.api_key import set_api_key
from napari_chatgpt.llm.llm import LLM

if TYPE_CHECKING:
    from litemind.apis.combined_api import CombinedApi

__litemind_api = None


def is_llm_available() -> bool:
    """
    Checks if the LiteMind API is available.

    This function checks if the global LiteMind API instance is initialized.
    If it is not initialized, it will return False, indicating that the API
    is not available.

    Returns:
        bool: True if the LiteMind API is available, False otherwise.
    """
    try:
        # Check that the list API_IMPLEMENTATIONS contains at least one API implementation except for DefaultApi and CombinedApi:
        from litemind import API_IMPLEMENTATIONS

        api_implementations = list(API_IMPLEMENTATIONS)

        # Remove DefaultApi and CombinedApi from the list:
        from litemind.apis.combined_api import CombinedApi
        from litemind.apis.default_api import DefaultApi

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

    except (ImportError, ModuleNotFoundError):
        # If any required module is not installed (e.g., docling), return False
        return False


def _register_api(combined_api: "CombinedApi", api) -> bool:
    """Register an API instance into a CombinedApi's model_to_api map.

    Parameters
    ----------
    combined_api : CombinedApi
        The combined API to register into.
    api : BaseApi
        The API instance to register.

    Returns
    -------
    bool
        True if the API was registered with at least one model.
    """
    try:
        models = api.list_models()
        if not models:
            return False
        for model in models:
            if model not in combined_api.model_to_api:
                combined_api.model_to_api[model] = api
        combined_api.apis.append(api)
        return True
    except Exception as e:
        aprint(f"Failed to register API {api.__class__.__name__}: {e}")
        return False


def _build_custom_apis(combined_api: "CombinedApi") -> None:
    """Register custom OpenAI-compatible endpoints and GitHub Models.

    Reads ``custom_endpoints`` from ``AppConfiguration("omega")``
    (stored in ``~/.omega/config.yaml``). Each entry must specify
    ``base_url`` and ``api_key_env``.

    Also auto-detects ``GITHUB_TOKEN`` and registers GitHub Models
    (``https://models.inference.ai.azure.com``) when available.
    """
    from napari_chatgpt.utils.configuration.app_configuration import AppConfiguration

    config = AppConfiguration("omega")

    # --- Custom endpoints from config ---
    custom_endpoints = config["custom_endpoints"] or []
    if custom_endpoints:
        from litemind.apis.providers.openai.openai_api import OpenAIApi

        for endpoint in custom_endpoints:
            name = endpoint.get("name", "custom")
            base_url = endpoint.get("base_url")
            api_key_env = endpoint.get("api_key_env")

            if not base_url:
                aprint(f"Skipping custom endpoint '{name}': missing base_url")
                continue

            api_key = os.environ.get(api_key_env, "") if api_key_env else ""
            if not api_key:
                aprint(
                    f"Skipping custom endpoint '{name}': "
                    f"env var '{api_key_env}' not set"
                )
                continue

            try:
                with asection(f"Registering custom endpoint: {name}"):
                    api = OpenAIApi(api_key=api_key, base_url=base_url)
                    if _register_api(combined_api, api):
                        aprint(f"Custom endpoint '{name}' registered successfully")
                    else:
                        aprint(f"Custom endpoint '{name}': no models available")
            except Exception as e:
                aprint(f"Failed to register custom endpoint '{name}': {e}")

    # --- GitHub Models auto-detection ---
    github_token = os.environ.get("GITHUB_TOKEN", "")
    if github_token:
        try:
            from litemind.apis.providers.openai.openai_api import OpenAIApi

            with asection("Registering GitHub Models"):
                api = OpenAIApi(
                    api_key=github_token,
                    base_url="https://models.inference.ai.azure.com",
                )
                if _register_api(combined_api, api):
                    aprint("GitHub Models registered successfully")
                else:
                    aprint("GitHub Models: no models available")
        except Exception as e:
            aprint(f"Failed to register GitHub Models: {e}")


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

        # Register custom endpoints and GitHub Models:
        _build_custom_apis(__litemind_api)

    return __litemind_api


@lru_cache
def get_model_list() -> list[str]:
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


def has_model_support_for(model_name: str, features: list[ModelFeatures]) -> bool:
    """
    Checks if a specific model supports the given features.

    Parameters
    ----------
    model_name: str
        The name of the model to check.
    features: List[ModelFeatures]
        A list of features to check for support.

    Returns
    -------
    bool: True if the model supports all specified features, False otherwise.
    """
    api = get_litemind_api()
    return api.has_model_support_for(features=features, model_name=model_name)


def get_llm(
    model_name: str | None = None,
    temperature: float = 0.0,
    features: list[ModelFeatures] | None = None,
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
