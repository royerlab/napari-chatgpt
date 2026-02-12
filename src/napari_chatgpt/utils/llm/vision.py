"""Vision utilities for checking model capabilities and describing images via LLM."""

from arbol import aprint, asection
from litemind import CombinedApi
from litemind.apis.base_api import BaseApi
from litemind.apis.model_features import ModelFeatures


def is_vision_available(
    api: BaseApi | None = None,
    model_name: str | None = None,
) -> bool:
    """Check if vision is available.

    Args:
        api: API to use for checking availability. If None, uses CombinedApi.
        model_name: Specific model name to check for vision capabilities.
            If None, checks all models.

    Returns:
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
    api: BaseApi | None = None,
    model_name: str | None = None,
    number_of_tries: int = 4,
) -> str:
    """Describe an image using GPT-vision.

    Args:
        image_path: Path to the image to describe.
        query: Query to send to GPT.
        api: API to use for describing the image. If None, uses CombinedApi.
        model_name: Model to use.
        number_of_tries: Number of times to try to send the request to GPT.

    Returns:
        Description of the image.
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
