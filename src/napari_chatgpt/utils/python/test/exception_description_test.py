from arbol import aprint

from napari_chatgpt.utils.python.exception_description import (
    exception_description,
)


def test_exceptions_description():
    try:
        # Your code here
        # This is where the error occurs
        raise ValueError("Example error")
    except Exception as e:
        description = exception_description(e)
        aprint(description)

        assert "Example error" in description
        assert "(ValueError)" in description
        assert 'raise ValueError("Example error")' in description


def test_exception_with_out_of_range_line_number():
    """IndexError from out-of-range line number is caught gracefully."""
    from unittest.mock import mock_open, patch

    from napari_chatgpt.utils.python.exception_description import (
        exception_info,
    )

    try:
        raise TypeError("bad type")
    except Exception as e:
        # Mock open to return a 1-line file so the traceback's
        # line number (which will be > 1) triggers IndexError:
        m = mock_open(read_data="only one line\n")
        with patch("builtins.open", m):
            info = exception_info(e)

        assert info["exception_name"] == "TypeError"
        assert "bad type" in info["exception_message"]
        assert "code line unavailable" in info["error_line"]


def test_find_root_cause_depth_limit():
    """Test that find_root_cause handles deep chains without stack overflow."""
    from napari_chatgpt.utils.python.exception_description import (
        find_root_cause,
    )

    # Build a chain of 150 exceptions (exceeds the 100 depth limit):
    root = ValueError("root")
    current = root
    for i in range(150):
        new_exc = RuntimeError(f"level {i}")
        new_exc.__cause__ = current
        current = new_exc

    # Should not raise RecursionError:
    result = find_root_cause(current)
    # It should stop at depth 100, not necessarily reaching the root:
    assert result is not None
