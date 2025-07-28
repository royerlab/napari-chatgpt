import traceback

from arbol import asection, aprint

from napari_chatgpt.llm.api_keys.api_key import set_api_key


def get_openai_model_list(filter: str = "gpt", verbose: bool = False) -> list:
    """
    Retrieve a filtered list of available OpenAI ChatGPT model IDs.
    
    Parameters:
        filter (str): Substring to filter model IDs. Only models containing this substring are included.
        verbose (bool): If True, prints each included model ID.
    
    Returns:
        list: List of filtered model IDs, excluding those related to vision, instruct, turbo-instruct, preview, realtime, audio, transcribe, or image. Returns an empty list if an error occurs.
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
                f"Error: {type(e).__name__} with message: '{str(e)}' occured while trying to get the list of OpenAI models. "
            )
            # print stacktrace:
            traceback.print_exc()

            return []


def postprocess_openai_model_list(model_list: list) -> list:
    """
    Refines and reorders a list of OpenAI model IDs by removing problematic models and prioritizing higher-quality ones.
    
    The function excludes models known to be less desirable or unsupported, then reorders the list to place preferred models (such as those containing "gpt-4o" and other high-quality identifiers) at the top.
    
    Parameters:
        model_list (list): List of OpenAI model IDs to process.
    
    Returns:
        list: The filtered and reordered list of model IDs.
    """

    try:
        # First, sort the list of models:
        model_list = sorted(model_list)

        # get list of bad models for main LLM:
        bad_models_filters = {
            "0613",
            "vision",
            "turbo-instruct",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-0301",
            "gpt-3.5-turbo-1106",
            "gpt-3.5-turbo-0125",
            "gpt-3.5-turbo-16k",
            "chatgpt-4o-latest",
        }

        # get list of best models for main LLM:
        best_models_filters = {"0314", "0301", "1106", "gpt-4", "gpt-4o"}

        # Ensure that some 'bad' or unsupported models are excluded:
        bad_models = [
            m for m in model_list if any(bm in m for bm in bad_models_filters)
        ]
        for bad_model in bad_models:
            if bad_model in model_list:
                model_list.remove(bad_model)
                # model_list.append(bad_model)

        # Ensure that the best models are at the top of the list:
        best_models = [
            m for m in model_list if any(bm in m for bm in best_models_filters)
        ]
        model_list = best_models + [m for m in model_list if m not in best_models]

        # Ensure that the very best models are at the top of the list:
        very_best_models = [
            m for m in model_list if ("gpt-4o" in m and "mini" not in m)
        ]
        model_list = very_best_models + [
            m for m in model_list if m not in very_best_models
        ]

    except Exception as exc:
        aprint(f"Error occurred: {exc}")

        # print stacktrace:
        traceback.print_exc()

    return model_list
