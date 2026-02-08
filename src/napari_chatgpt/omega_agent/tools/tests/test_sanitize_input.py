from napari_chatgpt.omega_agent.tools.special.python_repl import sanitize_input


def test_backtick_removal():
    assert sanitize_input("`print(1)`") == "print(1)"


def test_python_prefix_removal():
    assert sanitize_input("python print(1)") == "print(1)"


def test_combined_backticks_and_python():
    assert sanitize_input("```python\nprint(1)\n```") == "print(1)"


def test_whitespace_trimming():
    assert sanitize_input("  print(1)  ") == "print(1)"


def test_clean_input_unchanged():
    assert sanitize_input("print(1)") == "print(1)"


def test_empty_input():
    assert sanitize_input("") == ""


def test_whitespace_only():
    assert sanitize_input("   ") == ""
