from typing import Optional

from arbol import asection, aprint
from litemind import CombinedApi
from litemind.apis.base_api import BaseApi
from litemind.apis.model_features import ModelFeatures


def is_vision_available(
    api: Optional[BaseApi] = None,
    model_name: Optional[str] = None,
) -> bool:
    """
    Check if vision is available.

    Parameters
    ----------
    api : BaseApi, optional
        API to use for checking availability. If None, uses CombinedApi.
    model_name : str, optional
        Specific model name to check for vision capabilities. If None, checks all models.

    Returns
    -------
    bool
        True if the model is available, False otherwise.

    """

    with asection(f"Checking if vision is available:"):
        try:
            if api is None:
                api = CombinedApi()

            if model_name is None:
                model_name = api.get_best_model(
                    features=[ModelFeatures.TextGeneration, ModelFeatures.Image]
                )

            return model_name and api.has_model_support_for(
                model_name=model_name,
                features=[ModelFeatures.TextGeneration, ModelFeatures.Image],
            )
        except Exception as e:
            # Print stacktrace:
            import traceback

            traceback.print_exc()
            # Log the error:
            aprint(f"Error while checking vision availability: {e}")
            # Return False if there was an error:
            return False


def describe_image(
    image_path: str,
    query: str = "Here is an image, please carefully describe it in detail.",
    api: Optional[BaseApi] = None,
    model_name: Optional[str] = None,
    number_of_tries: int = 4,
) -> str:
    """
    Describe an image using GPT-vision.

    Parameters
    ----------
    image_path: str
        Path to the image to describe
    query  : str
        Query to send to GPT
    model_name   : str
        Model to use
    max_tokens  : int
        Maximum number of tokens to use
    number_of_tries : int
        Number of times to try to send the request to GPT.

    Returns
    -------
    str
        Description of the image

    """

    with asection(f"Describe a given image at path: '{image_path}':"):
        try:
            if api is None:
                api = CombinedApi()

            if model_name is None or not api.has_model_support_for(
                model_name=model_name,
                features=[ModelFeatures.TextGeneration, ModelFeatures.Image],
            ):
                model_name = api.get_best_model(
                    features=[ModelFeatures.TextGeneration, ModelFeatures.Image]
                )

            # Convert image path to URI:
            image_uri = (
                "file://" + image_path
                if not image_path.startswith("http")
                else image_path
            )

            description = api.describe_image(
                image_uri=image_uri,
                query=query,
                model_name=model_name,
                number_of_tries=number_of_tries,
            )

            if not description:
                raise ValueError(
                    f"No description returned for image at path: '{image_path}'"
                )
            else:
                description = description.strip()

            aprint(f"Image description: {description}")
            return description
        except Exception as e:
            # Print stacktrace:
            import traceback

            traceback.print_exc()
            # Log the error:
            aprint(f"Error while describing image: {e}")
            # Return a description of the error:
            description = (
                f"Failed to describe image at path: '{image_path}'. Error: {str(e)}"
            )
            return description
