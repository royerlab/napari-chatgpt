import pytest

from napari_chatgpt.utils.api_keys.api_key import is_api_key_available
from napari_chatgpt.utils.openai.gpt_vision import is_gpt_vision_available
from napari_chatgpt.utils.openai.model_list import get_openai_model_list


@pytest.mark.skipif(not is_api_key_available('OpenAI'),
                    reason="requires OpenAI key to run")
def test_model_list():
    model_list = get_openai_model_list()
    assert model_list and len(model_list) > 0