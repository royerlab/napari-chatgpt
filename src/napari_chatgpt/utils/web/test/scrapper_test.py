from arbol import aprint

from napari_chatgpt.utils.web.scrapper import text_from_url


def test_scrapper():
    # url = 'https://www.czbiohub.org/sf/people/staff/loic-royer-dr-rer-nat/'
    url = 'https://forum.image.sc/t/image-registration-in-python/51743'
    text = text_from_url(url)

    aprint(text)

    assert len(text) > 0
