from arbol import aprint

from napari_chatgpt.utils.python.exception_guard import ExceptionGuard


def test_exceptions_guard():
    try:
        with ExceptionGuard() as g:
            raise RuntimeError('something went wrong')
            pass

        aprint(g)

    except Exception as e:
        # We should not reach this point:
        assert False
