"""Retrieve and post-process the list of available OpenAI GPT models."""

import traceback

from arbol import aprint, asection

from napari_chatgpt.llm.api_keys.api_key import set_api_key


def get_openai_model_list(filter: str = "gpt", verbose: bool = False) -> list:
    """Get the list of all OpenAI ChatGPT models.

    Args:
        filter: Filter to apply to the list of models.
        verbose: Verbosity flag.

    Returns:
        List of models.
    """

    with asection(f"Enumerating all OpenAI ChatGPT models:"):

        # Ensure that the OpenAI API key is set:
        set_api_key("OpenAI")

        # Local imports to avoid issues:
        from openai import OpenAI

        try:
            # Model list to populate:
            model_list = []

            # Instantiate API entry point
            client = OpenAI()

            # Goes through models and populate the list:
            for model in client.models.list().data:
                model_id = model.id

                # only keep models that match the filter:
                if filter in model_id:
                    model_list.append(model_id)
                    if verbose:
                        aprint(model_id)

            # Remove any models that contain the following substrings:
            model_list = [
                m
                for m in model_list
                if not any(
                    x in m
                    for x in [
                        "vision",
                        "instruct",
                        "turbo-instruct",
                        "preview",
                        "realtime",
                        "audio",
                        "transcribe",
                        "image",
                    ]
                )
            ]

            return model_list

        except Exception as e:
            # Error message:
            aprint(
                f"Error: {type(e).__name__} with message: '{str(e)}' occurred while trying to get the list of OpenAI models. "
            )
            # print stacktrace:
            traceback.print_exc()

            return []


def postprocess_openai_model_list(model_list: list) -> list:
    """Postprocess the list of OpenAI models.

    This is useful to remove problematic models from the list and sort models
    in decreasing order of quality.

    Args:
        model_list: List of models.

    Returns:
        Postprocessed list of models.
    """

    try:
        # Substrings that mark models to exclude entirely:
        excluded_filters = {
            "0613",
            "vision",
            "turbo-instruct",
            "gpt-3.5",
            "chatgpt-4o-latest",
        }

        # Remove excluded models:
        model_list = [
            m for m in model_list if not any(ex in m for ex in excluded_filters)
        ]

        # Preferred substrings, most recent first:
        preferred = [
            "gpt-5.2",
            "gpt-5.1",
            "gpt-5",
            "gpt-4.1",
            "gpt-4o",
        ]

        def _sort_key(model: str) -> tuple[int, str]:
            for tier, sub in enumerate(preferred):
                if sub in model:
                    return (tier, model)
            return (len(preferred), model)

        model_list.sort(key=_sort_key)

    except Exception as exc:
        aprint(f"Error occurred: {exc}")
        traceback.print_exc()

    return model_list
