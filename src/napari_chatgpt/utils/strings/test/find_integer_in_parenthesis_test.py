from napari_chatgpt.utils.strings.find_integer_in_parenthesis import \
    find_integer_in_parenthesis


def test_find_integer_in_parenthesis():
    # Test the function.
    string = "some text (3) and more here"
    text, integer = find_integer_in_parenthesis(string)

    assert text == "some text  and more here"
    assert integer == 3
