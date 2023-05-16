import random
import re
import time
from typing import Optional

from bs4 import BeautifulSoup
from bs4.element import Comment
from requests import Session

from napari_chatgpt.utils.web.headers import _scrapping_request_headers


def _tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta',
                               '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(body,
                   cleanup: bool = True,
                   max_text_snippets: Optional[int] = None,
                   min_words: int = 5,
                   sort_snippets_by_decreasing_size: bool = True,
                   ):
    # Instantiates a BeautifulSoup scrapper:
    soup = BeautifulSoup(body, 'html.parser')

    # scraps all text snippets from page:
    texts = soup.findAll(text=True)

    # Removes text that is not visible on the page:
    visible_texts = filter(_tag_visible, texts)

    if cleanup:
        # Strips text snippets from trailing white spaces:
        visible_texts = [text.strip() for text in visible_texts]

        # Filters text snippets that are too short:
        visible_texts = [text for text in visible_texts if
                         len(text.split()) >= min_words]

    # Sorts the text snippets in decreasing order of length:
    if sort_snippets_by_decreasing_size:
        visible_texts = sorted(visible_texts, key=lambda x: len(x),
                               reverse=True)

    # Limits the number of text snippets:
    if max_text_snippets:
        visible_texts = visible_texts[0:max_text_snippets]

    # Assembles the text snippets:
    text = u"\n----\n".join(t.strip() for t in visible_texts)

    if cleanup:
        # Replaces multiple next lines to a single one:
        text = re.sub("\n\n+", "\n", text)

        # replaces any other kind of repeated whitespace to a single space:
        text = re.sub("\s\s+", " ", text)

    return text


def _current_time_ms():
    current_time = round(time.time() * 1000)
    return current_time


_last_query_time_ms = _current_time_ms()


def text_from_url(url: str,
                  cleanup: bool = True,
                  max_text_snippets: int = None,
                  min_words_per_snippet: int = 5,
                  sort_snippets_by_decreasing_size: bool = True,
                  max_query_freq_hz: float = 100) -> str:
    with Session() as session:
        # Instantiates a session so that websites that request to set cookies can be happy:
        response = session.get(url, headers=_scrapping_request_headers)

        # Get the contents of the page:
        html = response.text

        # Extracts visible and readable text from page:
        text = text_from_html(html,
                              cleanup=cleanup,
                              max_text_snippets=max_text_snippets,
                              min_words=min_words_per_snippet,
                              sort_snippets_by_decreasing_size=sort_snippets_by_decreasing_size
                              )

        # Random waiting to avoid issues:
        wait_time_ms = round(
            ((1000 / max_query_freq_hz) - 100) * random.random() + 100)
        deadline_ms = _last_query_time_ms + wait_time_ms

        # Release wait if deadline passed:
        while _current_time_ms() < deadline_ms:
            time.sleep(0.005)

        return text
