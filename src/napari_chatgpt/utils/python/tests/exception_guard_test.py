"""Tests for ExceptionGuard context manager."""

from napari_chatgpt.utils.python.exception_guard import ExceptionGuard


def test_exceptions_guard():
    try:
        with ExceptionGuard() as g:
            raise RuntimeError("something went wrong")

        # Guard should have caught it, so no exception propagated
        assert g.exception is not None

    except Exception:
        # We should not reach this point:
        assert False


def test_exception_guard_stores_state():
    with ExceptionGuard(print_stacktrace=False) as g:
        raise ValueError("test msg")

    assert g.exception == ValueError
    assert g.exception_type_name == "ValueError"
    assert str(g.exception_value) == "test msg"
    assert g.exception_traceback is not None
    assert "ValueError" in g.exception_description


def test_exception_guard_no_exception():
    with ExceptionGuard() as g:
        pass

    assert g.exception is None
    assert g.exception_type_name is None
    assert g.exception_value is None
    assert g.exception_traceback is None
