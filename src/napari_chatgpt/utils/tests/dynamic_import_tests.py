import os
import tempfile

from arbol import aprint

from napari_chatgpt.utils.dynamic_import import dynamic_import
from src.napari_chatgpt.utils.download_files import download_files
from src.napari_chatgpt.utils.extract_urls import extract_urls

__some_register={}

___module_code = """
def my_function(x): return x**2
print('test_dynamic_import')
"""

def test_dynamic_import():

    # Dynamic import and execution:
    module = dynamic_import(___module_code)

    exec("__some_register['my_function'] = module.my_function")

    assert __some_register['my_function'](2) == 4




