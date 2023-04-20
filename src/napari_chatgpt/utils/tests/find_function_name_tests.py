import os
import tempfile

from arbol import aprint

from napari_chatgpt.utils.dynamic_import import dynamic_import
from napari_chatgpt.utils.find_function_name import find_function_name
from src.napari_chatgpt.utils.download_files import download_files
from src.napari_chatgpt.utils.extract_urls import extract_urls

__some_register={}

_some_code = """
import this and that
import numpy as np
def my_function(x): return x**2
print('test_dynamic_import')
#more code
"""

def test_find_function_name():

    function_name = find_function_name(_some_code)

    assert function_name == 'my_function'


