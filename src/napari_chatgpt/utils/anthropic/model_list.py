import traceback

from arbol import asection, aprint

from napari_chatgpt.utils.api_keys.api_key import set_api_key




def get_anthropic_model_list() -> list:
    """
    Get the list of all Anthropic  models.

    Parameters
    ----------
    filter : str
        Filter to apply to the list of models.
    Returns
    -------
    list
        List of models.

    """

    with asection("Enumerating all Anthropic models:"):
        model_list = []

        model_list.append('claude-3-opus-20240229')
        model_list.append('claude-3-sonnet-20240229')
        model_list.append('claude-3-haiku-20240307')
        model_list.append('claude-3-5-sonnet-20240620')

        return model_list



