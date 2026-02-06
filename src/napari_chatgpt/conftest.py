"""Root conftest.py with shared test fixtures for napari-chatgpt."""

import pytest


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
