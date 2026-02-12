"""Web scraping utilities for extracting visible text from HTML pages."""

import random
import re
import time

from bs4 import BeautifulSoup
from bs4.element import Comment
from requests import Session

from napari_chatgpt.utils.web.headers import _scrapping_request_headers


def _tag_visible(element):
    """Check whether a BeautifulSoup element is visible on the page.

    Filters out elements inside non-visible tags (style, script, head,
    meta, etc.) and HTML comments.

    Args:
        element: A BeautifulSoup NavigableString element.

    Returns:
        True if the element would be visible to a user, False otherwise.
    """
    if element.parent.name in [
        "style",
        "script",
        "head",
        "title",
        "meta",
        "[document]",
    ]:
        return False
    if isinstance(element, Comment):
        return False
    return True


def text_from_html(
    body,
    cleanup: bool = True,
    max_text_snippets: int | None = None,
    min_words: int = 5,
    sort_snippets_by_decreasing_size: bool = True,
):
    """Extract visible text from an HTML document body.

    Parses HTML, extracts all visible text snippets, and optionally
    cleans, filters, sorts, and limits them.

    Args:
        body: Raw HTML string to parse.
        cleanup: If True, strip whitespace, remove short snippets,
            and collapse repeated whitespace in the output.
        max_text_snippets: Maximum number of text snippets to include.
            None means no limit.
        min_words: Minimum word count for a snippet to be kept
            (only applies when cleanup is True).
        sort_snippets_by_decreasing_size: If True, sort snippets by
            length in descending order before limiting.

    Returns:
        A single string with extracted text snippets separated by
        '----' delimiters.
    """
    # Instantiates a BeautifulSoup scrapper:
    soup = BeautifulSoup(body, "html.parser")

    # scraps all text snippets from page:
    texts = soup.find_all(string=True)

    # Removes text that is not visible on the page:
    visible_texts = filter(_tag_visible, texts)

    if cleanup:
        # Strips text snippets from trailing white spaces:
        visible_texts = [text.strip() for text in visible_texts]

        # Filters text snippets that are too short:
        visible_texts = [
            text for text in visible_texts if len(text.split()) >= min_words
        ]

    # Sorts the text snippets in decreasing order of length:
    if sort_snippets_by_decreasing_size:
        visible_texts = sorted(visible_texts, key=lambda x: len(x), reverse=True)

    # Limits the number of text snippets:
    if max_text_snippets:
        visible_texts = visible_texts[0:max_text_snippets]

    # Assembles the text snippets:
    text = "\n----\n".join(t.strip() for t in visible_texts)

    if cleanup:
        # Replaces multiple next lines to a single one:
        text = re.sub("\n\n+", "\n", text)

        # replaces any other kind of repeated whitespace to a single space:
        text = re.sub(r"\s\s+", " ", text)

    return text


def _current_time_ms():
    """Return the current time in milliseconds."""
    current_time = round(time.time() * 1000)
    return current_time


_last_query_time_ms = _current_time_ms()


def text_from_url(
    url: str,
    cleanup: bool = True,
    max_text_snippets: int = None,
    min_words_per_snippet: int = 5,
    sort_snippets_by_decreasing_size: bool = True,
    max_query_freq_hz: float = 100,
) -> str:
    """Fetch a URL and extract its visible text content.

    Downloads the page, extracts visible text using BeautifulSoup,
    and applies rate limiting to avoid overwhelming servers.

    Args:
        url: The URL to fetch and scrape.
        cleanup: If True, clean up whitespace and filter short snippets.
        max_text_snippets: Maximum number of text snippets to return.
        min_words_per_snippet: Minimum word count per snippet.
        sort_snippets_by_decreasing_size: If True, sort snippets by
            length in descending order.
        max_query_freq_hz: Maximum query frequency in Hz for rate
            limiting between successive calls.

    Returns:
        Extracted visible text from the page as a single string.
    """
    global _last_query_time_ms

    with Session() as session:
        # Instantiates a session so that websites that request to set cookies can be happy:
        response = session.get(url, headers=_scrapping_request_headers)

        # Get the contents of the page:
        html = response.text

        # Extracts visible and readable text from page:
        text = text_from_html(
            html,
            cleanup=cleanup,
            max_text_snippets=max_text_snippets,
            min_words=min_words_per_snippet,
            sort_snippets_by_decreasing_size=sort_snippets_by_decreasing_size,
        )

        # Random waiting to avoid issues:
        wait_time_ms = round(((1000 / max_query_freq_hz) - 100) * random.random() + 100)
        deadline_ms = _last_query_time_ms + wait_time_ms

        # Release wait if deadline passed:
        while _current_time_ms() < deadline_ms:
            time.sleep(0.005)

        # Update the last query time for rate limiting
        _last_query_time_ms = _current_time_ms()

        return text
