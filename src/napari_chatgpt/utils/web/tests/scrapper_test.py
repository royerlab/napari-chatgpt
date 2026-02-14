import pytest

from napari_chatgpt.utils.web.scrapper import text_from_html, text_from_url


@pytest.mark.integration
def test_scrapper():
    url = "https://forum.image.sc/t/image-registration-in-python/51743"
    try:
        text = text_from_url(url)
        assert len(text) > 0
    except Exception as e:
        pytest.skip(f"URL fetch failed: {e}")


def test_text_from_html_excludes_script_and_style(sample_html):
    text = text_from_html(sample_html)
    assert "alert" not in text
    assert "color: red" not in text


def test_text_from_html_excludes_comments(sample_html):
    text = text_from_html(sample_html)
    assert "This is a comment" not in text


def test_text_from_html_min_words_filter():
    html = "<html><body><p>Short.</p><p>This paragraph has enough words to survive the filter.</p></body></html>"
    text = text_from_html(html, cleanup=True, min_words=5)
    assert "Short." not in text
    assert "enough words" in text


def test_text_from_html_max_text_snippets(sample_html):
    text = text_from_html(sample_html, max_text_snippets=2)
    # With max_text_snippets=2, should only have 2 snippets separated by ----
    parts = text.split("----")
    assert len(parts) <= 2


def test_text_from_html_sort_by_decreasing_size(sample_html):
    text = text_from_html(sample_html, sort_snippets_by_decreasing_size=True)
    parts = [p.strip() for p in text.split("----") if p.strip()]
    if len(parts) >= 2:
        assert len(parts[0]) >= len(parts[1])


def test_text_from_html_no_cleanup():
    html = "<html><body><p>  spaces  here  </p></body></html>"
    text = text_from_html(html, cleanup=False, sort_snippets_by_decreasing_size=False)
    # With cleanup=False, whitespace should be preserved in the output
    assert "spaces" in text


def test_text_from_html_empty_body():
    text = text_from_html("")
    assert text == ""


def test_text_from_html_only_invisible():
    html = "<html><head><script>var x=1;</script><style>.a{}</style></head><body></body></html>"
    text = text_from_html(html, cleanup=True, min_words=3)
    assert text == ""
