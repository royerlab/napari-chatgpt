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
    Determine whether a vision-capable language model is available for use.
    
    Checks if the specified or best available model supports both text generation and image features. Returns False if an error occurs or if no suitable model is found.
    
    Returns:
        bool: True if a model supporting both text and image features is available; False otherwise.
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
    Generates a detailed textual description of an image using a vision-capable GPT model.
    
    Parameters:
        image_path (str): Path or URL to the image to be described.
        query (str, optional): Prompt to guide the description. Defaults to a detailed description request.
        model_name (str, optional): Specific model to use. If not provided or unsupported, the best available model is selected.
        number_of_tries (int, optional): Number of attempts to send the request. Defaults to 4.
    
    Returns:
        str: The generated image description, or an error message if the description could not be obtained.
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
