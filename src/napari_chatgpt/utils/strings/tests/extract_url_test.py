"""Tests for extract_urls()."""

from napari_chatgpt.utils.strings.extract_urls import extract_urls


def test_extract_urls():
    text = (
        "Check out my website at https://www.example.com! "
        "For more information, visit http://en.wikipedia.org/wiki/URL."
    )
    urls = extract_urls(text)

    assert len(urls) == 2
    assert "https://www.example.com" in urls
    assert "http://en.wikipedia.org/wiki/URL" in urls


def test_extract_urls_no_urls():
    text = "No URLs here at all."
    urls = extract_urls(text)
    assert len(urls) == 0


def test_extract_urls_single():
    text = "Visit https://example.com for details."
    urls = extract_urls(text)
    assert len(urls) == 1
    assert "https://example.com" in urls
