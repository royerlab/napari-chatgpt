from napari_chatgpt.utils.strings.find_function_name import find_function_name

__some_register = {}

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
