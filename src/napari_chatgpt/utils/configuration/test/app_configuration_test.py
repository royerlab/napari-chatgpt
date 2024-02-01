import pytest
from arbol import aprint

from napari_chatgpt.utils.api_keys.api_key import is_api_key_available
from napari_chatgpt.utils.llm.summarizer import summarize
from napari_chatgpt.utils.web.scrapper import text_from_url
from napari_chatgpt.utils.configuration.app_configuration import \
    AppConfiguration


def test_app_configuration():

    default_config = {'test_key_2':'default_value'}

    config_1 = AppConfiguration('test_app_configuration', default_config=default_config)

    assert config_1['test_key_2'] == 'default_value'
    config_1['test_key'] = 'test_value'
    assert config_1['test_key'] == 'test_value'
    config_1['test_key'] = 'test_value2'
    assert config_1['test_key'] == 'test_value2'

    config_2 = AppConfiguration('test_app_configuration')
    assert config_2['test_key'] == 'test_value2'
    assert config_2['test_key_2'] == 'default_value'




