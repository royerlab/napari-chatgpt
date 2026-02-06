"""Root conftest.py with shared test fixtures for napari-chatgpt."""

from queue import Queue
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_queue_pair():
    """Returns a (to_queue, from_queue) pair of Queue objects."""
    return Queue(), Queue()


@pytest.fixture
def mock_llm():
    """A MagicMock spec'd to the LLM class with .generate() returning a mock message list."""
    from napari_chatgpt.llm.llm import LLM

    llm = MagicMock(spec=LLM)
    mock_message = MagicMock()
    mock_message.to_plain_text.return_value = "mock response"
    llm.generate.return_value = [mock_message]
    return llm


@pytest.fixture
def sample_python_code():
    """A simple valid Python code string for code manipulation tests."""
    return (
        "import numpy as np\n"
        "\n"
        "def add(a, b):\n"
        "    return a + b\n"
        "\n"
        "result = add(1, 2)\n"
    )


@pytest.fixture
def sample_html():
    """A crafted HTML string with script/style/visible text for scrapper tests."""
    return (
        "<html><head><title>Test</title>"
        "<style>body { color: red; }</style>"
        "<script>alert('hi');</script>"
        "</head><body>"
        "<!-- This is a comment -->"
        "<p>This is a paragraph with enough words to pass the filter.</p>"
        "<p>Short.</p>"
        "<p>Another paragraph that has many words and should be long enough to survive filtering.</p>"
        "<p>A third paragraph with several words for testing maximum snippets feature here.</p>"
        "<p>Fourth paragraph that also contains multiple words for the decreasing size sort test.</p>"
        "<p>Fifth paragraph added here with enough words to make it past the minimum word threshold.</p>"
        "</body></html>"
    )


@pytest.fixture
def tmp_config_dir(tmp_path):
    """A tmp_path based fixture for tests that create config files."""
    config_dir = tmp_path / "test_config"
    config_dir.mkdir()
    return config_dir
