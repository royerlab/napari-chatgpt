"""Google search utilities, vendored from googlesearch library.

Code vendored from:
https://github.com/Nv7-GitHub/googlesearch/blob/master/googlesearch/__init__.py
"""

import random

from napari_chatgpt.utils.web.headers import _scrapping_request_headers
from napari_chatgpt.utils.web.scrapper import text_from_url

_useragent_list = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) Gecko/20100101 Firefox/66.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0",
]


def _get_useragent():
    """Return a randomly selected browser User-Agent string."""
    return random.choice(_useragent_list)


from time import sleep

from bs4 import BeautifulSoup
from requests import get


def _req(term, results, lang, start, timeout):
    """Send a search request to Google and return the HTTP response.

    Args:
        term: The URL-encoded search term.
        results: Number of results to request.
        lang: Language code for the search (e.g., "en").
        start: Pagination offset for results.
        timeout: Request timeout in seconds.

    Returns:
        The HTTP response object from the Google search request.

    Raises:
        requests.HTTPError: If the response status code indicates an error.
    """
    headers = {**_scrapping_request_headers}
    headers["User-Agent"] = _get_useragent()

    resp = get(
        url="https://www.google.com/search",
        headers=headers,
        params={
            "q": term,
            "num": results + 2,  # Prevents multiple requests
            "hl": lang,
            "start": start,
        },
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp


class SearchResult:
    """A single Google search result with URL, title, and description.

    Attributes:
        url: The URL of the search result.
        title: The title text of the search result.
        description: The description snippet of the search result.
    """

    def __init__(self, url, title, description):
        self.url = url
        self.title = title
        self.description = description

    def __repr__(self):
        return f"SearchResult(url={self.url}, title={self.title}, description={self.description})"


def search_overview(
    query: str,
    num_results: int = 3,
    lang: str = "en",
    max_text_snippets: int = 5,
    max_query_freq_hz: float = 0.5,
) -> str:
    """Get a text overview of Google search results by scraping the results page.

    Args:
        query: The search query string.
        num_results: Number of results to request from Google.
        lang: Language code for the search (e.g., "en").
        max_text_snippets: Maximum number of text snippets to extract.
        max_query_freq_hz: Maximum query frequency in Hz for rate limiting.

    Returns:
        Extracted visible text from the Google search results page.
    """
    url = f"https://www.google.com/search?q={query}&num={num_results}&hl={lang}"
    text = text_from_url(
        url, max_text_snippets=max_text_snippets, max_query_freq_hz=max_query_freq_hz
    )
    return text


def search_google(
    query,
    num_results: int = 10,
    lang: str = "en",
    advanced: bool = False,
    sleep_interval: int = 0,
    timeout: int = 5,
) -> str:
    """Search Google and yield result URLs or SearchResult objects.

    Args:
        query: The search query string.
        num_results: Maximum number of results to return.
        lang: Language code for the search (e.g., "en").
        advanced: If True, yield SearchResult objects instead of
            plain URL strings.
        sleep_interval: Seconds to sleep between paginated requests.
        timeout: Request timeout in seconds.

    Yields:
        URL strings, or SearchResult objects if advanced is True.
    """

    escaped_term = query.replace(" ", "+")

    # Fetch
    start = 0
    fetched_pages = 0
    max_pages = 10
    while start < num_results and fetched_pages < max_pages:
        fetched_pages += 1
        # Send request
        resp = _req(escaped_term, num_results - start, lang, start, timeout)

        # Parse
        soup = BeautifulSoup(resp.text, "html.parser")
        result_block = soup.find_all("div", attrs={"class": "g"})
        for result in result_block:
            # Find link, title, description
            link = result.find("a", href=True)
            title = result.find("h3")
            description_box = result.find("div", {"style": "-webkit-line-clamp:2"})
            if description_box:
                description = description_box.text
                if link and title and description:
                    start += 1
                    if advanced:
                        yield SearchResult(link["href"], title.text, description)
                    else:
                        yield link["href"]
        sleep(sleep_interval)
