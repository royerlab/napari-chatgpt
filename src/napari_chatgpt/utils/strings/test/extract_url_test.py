from arbol import aprint

from napari_chatgpt.utils.strings.extract_urls import extract_urls


def test_extract_urls():
    text = "Check out my website at https://www.example.com! " \
           "For more information, visit http://en.wikipedia.org/wiki/URL."
    urls = extract_urls(text)
    aprint(urls)

    assert 'http://en.wikipedia.org/wiki/URL' in urls
