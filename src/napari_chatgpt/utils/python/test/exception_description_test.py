from arbol import aprint

from napari_chatgpt.utils.python.exception_description import \
    exception_description


def test_exceptions_description():
    try:
        # Your code here
        # This is where the error occurs
        raise ValueError("Example error")
    except Exception as e:
        description = exception_description(e)
        aprint(description)

        assert "Example error" in description
        assert '(ValueError)' in description
        assert 'raise ValueError("Example error")' in description
