import pytest
from arbol import aprint

from napari_chatgpt.utils.api_keys.api_key import is_api_key_available
from napari_chatgpt.utils.openai.gpt_vision import is_gpt_vision_available, \
    describe_image

@pytest.mark.skipif(not is_api_key_available('OpenAI'),
                    reason="requires OpenAI key to run")
def test_is_gpt_vision_available():
    assert is_gpt_vision_available()

@pytest.mark.skipif(not is_api_key_available('OpenAI') or not is_gpt_vision_available(),
                    reason="requires OpenAI key to run and availability of a vision model")
def test_gpt_vision():

    image_1_path = _get_image_path('python.png')

    description_1 = describe_image(image_1_path)

    print(description_1)

    assert 'snake' in description_1 and 'Python' in description_1

    image_2_path = _get_image_path('future.jpeg')

    description_2 = describe_image(image_2_path)

    print(description_2)

    assert 'futuristic' in description_2 and 'sunset' in description_2


def _get_image_path(image_name: str):
    import os

    # Get the directory of the current file
    current_dir = os.path.dirname(__file__)

    # Combine the two to get the absolute path
    absolute_path = os.path.join(current_dir, os.path.join('images/',image_name))

    aprint(absolute_path)
    return absolute_path
