from pprint import pprint

from napari_chatgpt.utils.python.dynamic_import import dynamic_import, \
    execute_as_module

__some_register = {}

___module_code = \
"""
def my_function(x): 
    return x**2
print('test_dynamic_import')
"""


def test_dynamic_import():
    # Dynamic import and execution:
    module = dynamic_import(___module_code)

    exec("__some_register['my_function'] = module.my_function")

    assert __some_register['my_function'](2) == 4


___some_numba_stuff = \
    """
    
    import numpy as np
    from numba import njit
    
    # Define a numba accelerated function to compute z-projection
    @njit
    def z_projection(image):
        return np.sum(image, axis=0)
    
    # Create a sample image
    image = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
    
    # Make sure we can pass stuff:
    image = image + external_var
    
    # Call the z_projection function
    result = z_projection(image)
    
    # Print the result
    print(result)
    
    """


def test_execute_as_module():
    result = execute_as_module(___some_numba_stuff, name='some_numba_stuff',
                               external_var=1)

    pprint(result)

    assert result == '[15 18 21]'
