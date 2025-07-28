from arbol import aprint

from napari_chatgpt.utils.openai.model_list import get_openai_model_list

# cache result of function:
_default_openai_model_name = None


def get_default_openai_model_name() -> str:
    # Check if the model name is in the cache:
    """
    Return the default OpenAI model name from the available models, prioritizing the latest version and shortest name.
    
    If a cached default model name exists, it is returned immediately. Otherwise, the function retrieves the list of available models, sorts them by descending version number (with special handling for versions containing 'o'), and ascending name length, then returns the top result. Returns None if no models are available.
    """
    global _default_openai_model_name
    if _default_openai_model_name is not None:
        aprint(f"Using cached default OpenAI model name: {_default_openai_model_name}")
        return _default_openai_model_name
    else:
        model_list = get_openai_model_list()

        if len(model_list) == 0:
            return None

        def model_key(model):
            # Split the model name into parts
            """
            Generate a sorting key for an OpenAI model name based on its version and name length.
            
            The key prioritizes models with higher version numbers (descending order) and, for equal versions, shorter model names (ascending order). If the version cannot be parsed as a float, the model is sorted last.
            
            Parameters:
                model (str): The OpenAI model name string to generate a sort key for.
            
            Returns:
                tuple: A tuple containing the negative float version (for descending sort) and the model name length.
            """
            parts = model.split("-")
            # Get the main version (e.g., '3.5' or '4' from 'gpt-3.5' or 'gpt-4')
            main_version = parts[1]

            if "o" in main_version:
                main_version = main_version.replace("o", ".25")

            # Use the length of the model name as a secondary sorting criterion
            length = len(model)
            # Sort by main version (descending), then by length (ascending)
            try:
                key = (-float(main_version), length)
            except Exception:
                # If conversion to float fails, return a tuple that ensures this model is sorted last
                key = (float("inf"), length)

            return key

        sorted_model_list = sorted(model_list, key=model_key)

        return sorted_model_list[0]
