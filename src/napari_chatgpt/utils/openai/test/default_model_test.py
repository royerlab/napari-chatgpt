import pytest

from napari_chatgpt.utils.api_keys.api_key import is_api_key_available
from napari_chatgpt.utils.openai.default_model import \
    get_default_openai_model_name
from napari_chatgpt.utils.openai.gpt_vision import is_gpt_vision_available


@pytest.mark.skipif(not is_api_key_available('OpenAI'),
                    reason="requires OpenAI key to run")
def test_default_model():
    assert 'gpt-3' in get_default_openai_model_name() or 'gpt-4' in get_default_openai_model_name()


