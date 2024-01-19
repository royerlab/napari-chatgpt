from arbol import aprint

from napari_chatgpt.utils.openai.model_list import get_openai_model_list

# cache result of function:
_default_openai_model_name = None

def get_default_openai_model_name() -> str:

    # Check if the model name is in the cache:
    global _default_openai_model_name
    if _default_openai_model_name is not None:
        aprint(f'Using cached default OpenAI model name: {_default_openai_model_name}')
        return _default_openai_model_name
    else:
        model_list = get_openai_model_list()
        def model_key(model):
            # Split the model name into parts
            parts = model.split('-')
            # Get the main version (e.g., '3.5' or '4' from 'gpt-3.5' or 'gpt-4')
            main_version = parts[1]
            # Use the length of the model name as a secondary sorting criterion
            length = len(model)
            # Sort by main version (descending), then by length (ascending)
            return (-float(main_version), length)

        sorted_model_list = sorted(model_list, key=model_key)

        return sorted_model_list[0]
