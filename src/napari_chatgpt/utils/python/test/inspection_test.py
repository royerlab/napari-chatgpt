from pprint import pprint

from napari_chatgpt.utils.python.inspection import enumerate_methods, \
    find_function_info_in_package, \
    get_function_info, object_info_str


def test_object_info():
    string = 'string'
    info = object_info_str(string)
    pprint(info)
    assert "Class <class 'str'>" in info


def test_enumerate_methods():
    a_string = 'string'
    methods = list(enumerate_methods(a_string))
    pprint(methods)
    assert len(methods) > 0
    assert 'capitalize' in methods[0]


def test_find_functions_in_package():
    convolve_functions = list(
        find_function_info_in_package('scipy', 'convolve'))
    pprint(convolve_functions)

    assert 'scipy.ndimage.convolve' in convolve_functions
    assert 'scipy.signal.signaltools.convolve' in convolve_functions


def test_find_functions_in_package():
    signature = get_function_info('scipy.ndimage.convolve')
    pprint(signature)

    assert 'scipy.ndimage.convolve' in signature
