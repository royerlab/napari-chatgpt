# Code Review: utils/web Package

**Review Date:** 2026-02-05
**Package Path:** `src/napari_chatgpt/utils/web/`
**Reviewer:** Claude Code Review

---

## Executive Summary

The `utils/web` package provides web scraping and search engine abstraction for the napari-chatgpt project. It includes modules for scraping web content, searching via Google and DuckDuckGo, Wikipedia lookups, and meta-search aggregation. While functional, the package exhibits several issues including incomplete type annotations, missing error handling, security considerations with URL handling, and inconsistent API design patterns.

---

## 1. Code Quality

### 1.1 Style Consistency

| Severity | Issue | Location |
|----------|-------|----------|
| **Low** | Misspelled module name | `scrapper.py` should be `scraper.py` |
| **Low** | Inconsistent import organization | `google.py:23-27` - imports placed after code block |
| **Low** | Leading underscore convention inconsistent | `headers.py:1` uses `_scrapping_request_headers` but `google.py:8` uses `_useragent_list` |
| **Low** | Comment refers to wrong module | `wikipedia.py:1` mentions "googlesearch" but uses DuckDuckGo |

#### Details

**scrapper.py** - Module naming:
```python
# File: scrapper.py (line 1)
# Should be renamed to scraper.py (standard English spelling)
```

**google.py:23-27** - Imports placed mid-file:
```python
"""googlesearch is a Python library for searching Google, easily."""
from time import sleep

from bs4 import BeautifulSoup
from requests import get
```
These imports should be at the top of the file with other imports.

**wikipedia.py:1** - Misleading comment:
```python
# Code vendored from: https://github.com/Nv7-GitHub/googlesearch/blob/master/googlesearch/__init__.py
```
This module uses DuckDuckGo, not the vendored Google search code. The comment is likely a copy-paste artifact.

### 1.2 Code Organization

| Severity | Issue | Location |
|----------|-------|----------|
| **Medium** | Global mutable state used for rate limiting | `scrapper.py:78` |
| **Medium** | No common base class or protocol for search engines | Package-wide |
| **Low** | Unused import | `duckduckgo.py:3-4` - `asection` imported but only `aprint` used in main functions |

**scrapper.py:78** - Global mutable state:
```python
_last_query_time_ms = _current_time_ms()
```
This global variable is never actually updated in `text_from_url()`, making the rate limiting logic ineffective.

---

## 2. Logic & Correctness

### 2.1 Bugs

| Severity | Issue | Location |
|----------|-------|----------|
| **High** | Rate limiting logic is broken | `scrapper.py:106-112` |
| **Medium** | Google search modifies shared headers dict | `google.py:31-32` |
| **Medium** | Infinite loop potential in Google search | `google.py:87-107` |
| **Low** | Return type annotation mismatch | `duckduckgo.py:41-55` |

**scrapper.py:106-112** - Broken rate limiting:
```python
def text_from_url(...):
    ...
    # Random waiting to avoid issues:
    wait_time_ms = round(((1000 / max_query_freq_hz) - 100) * random.random() + 100)
    deadline_ms = _last_query_time_ms + wait_time_ms  # Uses stale value!

    # Release wait if deadline passed:
    while _current_time_ms() < deadline_ms:
        time.sleep(0.005)

    return text  # _last_query_time_ms is NEVER updated!
```
The `_last_query_time_ms` is set once at module load and never updated. Each call computes a deadline based on the module load time, not the actual last query time. Fix: update `_last_query_time_ms` after each query.

**google.py:31-32** - Mutable headers modification:
```python
def _req(term, results, lang, start, timeout):
    headers = _scrapping_request_headers  # Reference to shared dict!
    headers["User-Agent"] = _get_useragent()  # Mutates shared dict
```
This modifies the shared `_scrapping_request_headers` dict imported from `headers.py`. Fix: use `headers = _scrapping_request_headers.copy()`.

**google.py:87-107** - Potential infinite loop:
```python
while start < num_results:
    resp = _req(escaped_term, num_results - start, lang, start, timeout)
    soup = BeautifulSoup(resp.text, "html.parser")
    result_block = soup.find_all("div", attrs={"class": "g"})
    for result in result_block:
        ...
        if description_box:
            description = description_box.text
            if link and title and description:
                start += 1  # Only increments when result is found
                ...
    sleep(sleep_interval)
```
If Google changes their HTML structure or returns no results matching the selector, `start` never increments and the loop runs forever.

**duckduckgo.py:41-55** - Return type mismatch:
```python
def search_ddg(
    query: str, num_results: int = 3, lang: str = "en", safe_search: str = "moderate"
) -> str:  # <-- Wrong: should be list[dict]
    ...
    return results  # Returns a list, not str
```

### 2.2 Edge Cases

| Severity | Issue | Location |
|----------|-------|----------|
| **Medium** | No handling for network timeouts | `scrapper.py:91` |
| **Medium** | No handling for HTTP errors | `scrapper.py:91` |
| **Medium** | Empty results handling incomplete | `duckduckgo.py:50-53` |
| **Low** | Division by zero possible | `scrapper.py:106` |

**scrapper.py:91** - No timeout or error handling:
```python
response = session.get(url, headers=_scrapping_request_headers)
# No timeout specified
# No exception handling for connection errors, timeouts, HTTP errors
```

**scrapper.py:106** - Division by zero:
```python
wait_time_ms = round(((1000 / max_query_freq_hz) - 100) * random.random() + 100)
```
If `max_query_freq_hz=0` is passed, this raises `ZeroDivisionError`.

---

## 3. Type Annotations

### 3.1 Missing Annotations

| Severity | Issue | Location |
|----------|-------|----------|
| **Medium** | Function missing return type | `scrapper.py:12-24` - `_tag_visible()` |
| **Medium** | Function missing return type | `scrapper.py:27-70` - `text_from_html()` |
| **Medium** | Function missing parameter types | `google.py:30` - `_req()` |
| **Medium** | Class missing type annotations | `google.py:49-56` - `SearchResult` |
| **Medium** | Function missing types | `google.py:73-107` - `search_google()` |
| **Low** | Parameter type mismatch | `scrapper.py:84` - `max_text_snippets: int = None` should be `int | None = None` |

**scrapper.py:12-24** - Missing types:
```python
def _tag_visible(element):  # Missing: element: Tag, return: bool
    if element.parent.name in [...]:
        return False
    ...
```

**google.py:30** - Missing parameter types:
```python
def _req(term, results, lang, start, timeout):  # All parameters untyped
```
Should be:
```python
def _req(term: str, results: int, lang: str, start: int, timeout: int) -> Response:
```

**google.py:49-56** - Class missing annotations:
```python
class SearchResult:
    def __init__(self, url, title, description):  # All untyped
        self.url = url
        self.title = title
        self.description = description
```

### 3.2 Incorrect Annotations

| Severity | Issue | Location |
|----------|-------|----------|
| **Medium** | Wrong return type | `duckduckgo.py:42-43` - Returns `list[dict]`, annotated as `str` |
| **Medium** | Return type inconsistent | `google.py:73-80` - Returns generator, annotated as `str` |

**google.py:73-80** - Generator typed as str:
```python
def search_google(
    query,
    num_results: int = 10,
    ...
) -> str:  # Wrong! It's a generator yielding str or SearchResult
    ...
    yield link["href"]  # or yield SearchResult(...)
```
Should be:
```python
def search_google(...) -> Generator[str | SearchResult, None, None]:
```

---

## 4. Documentation

### 4.1 Missing Docstrings

| Severity | Issue | Location |
|----------|-------|----------|
| **Medium** | No module docstring | `scrapper.py` |
| **Medium** | No module docstring | `headers.py` |
| **Medium** | No module docstring | `duckduckgo.py` |
| **Medium** | No module docstring | `metasearch.py` |
| **Medium** | No module docstring | `wikipedia.py` |
| **Low** | Function missing docstring | `scrapper.py:12` - `_tag_visible()` |
| **Low** | Function missing docstring | `scrapper.py:27` - `text_from_html()` |
| **Low** | Function missing docstring | `scrapper.py:81` - `text_from_url()` |
| **Low** | Function missing docstring | `duckduckgo.py:10` - `summary_ddg()` |
| **Low** | Function missing docstring | `duckduckgo.py:41` - `search_ddg()` |
| **Low** | Function missing docstring | `duckduckgo.py:58` - `search_images_ddg()` |
| **Low** | Function missing docstring | `wikipedia.py:7` - `search_wikipedia()` |
| **Low** | Function missing docstring | `metasearch.py:6` - `metasearch()` |

### 4.2 Comment Quality

| Severity | Issue | Location |
|----------|-------|----------|
| **Low** | Misleading comment | `wikipedia.py:1` |
| **Low** | Outdated vendoring notice | `google.py:1` |
| **Low** | Typo in comment | `scrapper.py:34` - "scrapper" should be "scraper" |
| **Low** | Comment doesn't match code | `scrapper.py:37` - "scraps" should be "scrapes" |

---

## 5. Architecture

### 5.1 Design Issues

| Severity | Issue | Location |
|----------|-------|----------|
| **Medium** | No common interface for search engines | Package-wide |
| **Medium** | Tight coupling with `summarize()` function | `duckduckgo.py`, `metasearch.py`, `wikipedia.py` |
| **Medium** | Mixed responsibilities in modules | `duckduckgo.py` combines search + summarization |
| **Low** | No abstraction for HTTP client | Uses raw `requests` throughout |

#### Recommendations

1. **Search Engine Protocol**: Define a common interface for search engines:
```python
from typing import Protocol

class SearchEngine(Protocol):
    def search(self, query: str, num_results: int = 10) -> list[SearchResult]: ...
```

2. **Separate concerns**: Move summarization logic out of search modules. The `summary_ddg()` function does two distinct things (search + summarize).

3. **HTTP Client Abstraction**: Create a configurable HTTP client with:
   - Configurable timeouts
   - Retry logic
   - Rate limiting
   - User-agent rotation

### 5.2 Dependency Management

| Severity | Issue | Location |
|----------|-------|----------|
| **Medium** | Runtime package installation | `duckduckgo.py:80-86` - `install_latest_ddg()` |
| **Low** | Tight coupling to `arbol` for logging | Throughout package |

**duckduckgo.py:80-86** - Runtime pip install:
```python
def install_latest_ddg():
    try:
        with asection("Installing the latest version of duckduckgo_search:"):
            aprint(pip_install_single_package("duckduckgo_search", upgrade=True))
    except Exception as e:
        traceback.print_exc()
```
Installing packages at runtime is generally discouraged. Better to document version requirements and fail with clear error messages.

---

## 6. Security

### 6.1 URL Handling

| Severity | Issue | Location |
|----------|-------|----------|
| **High** | No URL validation | `scrapper.py:81-113` |
| **High** | No URL sanitization | `google.py:66` |
| **Medium** | SSRF potential | `scrapper.py:91` |
| **Medium** | No redirect limit | `scrapper.py:91` |

**scrapper.py:81-113** - No URL validation:
```python
def text_from_url(url: str, ...):
    with Session() as session:
        response = session.get(url, headers=_scrapping_request_headers)
```
The URL is used directly without validation. An attacker could potentially:
- Use `file://` URLs to read local files
- Use internal IP addresses (SSRF)
- Use very long URLs to cause resource exhaustion

**Recommended mitigations:**
```python
from urllib.parse import urlparse

def validate_url(url: str) -> bool:
    parsed = urlparse(url)
    # Only allow http/https
    if parsed.scheme not in ('http', 'https'):
        raise ValueError(f"Invalid URL scheme: {parsed.scheme}")
    # Block internal IP ranges
    # Block localhost
    # Limit URL length
    return True
```

**google.py:66** - URL construction without encoding:
```python
url = f"https://www.google.com/search?q={query}&num={num_results}&hl={lang}"
```
The `query` is not URL-encoded. Should use `urllib.parse.quote()` or pass as params dict.

### 6.2 Input Validation

| Severity | Issue | Location |
|----------|-------|----------|
| **Medium** | No query sanitization | `google.py:83` |
| **Low** | No length limits on queries | Throughout |

**google.py:83** - Minimal query escaping:
```python
escaped_term = query.replace(" ", "+")
```
Only spaces are escaped. Other special characters could cause issues.

### 6.3 Information Disclosure

| Severity | Issue | Location |
|----------|-------|----------|
| **Low** | User-Agent reveals scraping intent | `headers.py:2` |
| **Low** | Outdated browser versions in UA strings | `google.py:8-16` |

**headers.py:2** - Outdated User-Agent:
```python
"User-Agent": "Mozilla/4.0 (X11; Linux x86_64) AppleWebKit/537.11 ..."
```
Mozilla/4.0 is very outdated and may trigger bot detection.

---

## 7. Test Coverage

### 7.1 Test Quality Analysis

| File | Tests | Coverage | Issues |
|------|-------|----------|--------|
| `scrapper_test.py` | 1 | Low | Only tests happy path |
| `google_test.py` | 1 | Low | No assertions, exception silently caught |
| `duckduckgo_test.py` | 2 | Medium | Handles rate limiting gracefully |
| `wikipedia_test.py` | 3 | Medium | Good skip conditions |
| `metasearch_test.py` | 2 | Low | Exception silently caught |

### 7.2 Test Issues

| Severity | Issue | Location |
|----------|-------|----------|
| **High** | Test catches exception and passes silently | `google_test.py:7-18` |
| **High** | Test catches exception and passes silently | `metasearch_test.py:25-37` |
| **Medium** | No unit tests with mocked HTTP | All test files |
| **Medium** | Tests depend on external services | All test files |
| **Low** | No edge case tests | All test files |
| **Low** | No error handling tests | All test files |

**google_test.py:7-18** - Silent exception handling:
```python
def test_google_search_overview():
    try:
        term = "wiki Mickey Mouse"
        text = search_overview(term)
        aprint(text)
        # No assertion here!
    except DuckDuckGoSearchException as e:
        aprint(f"DuckDuckGoSearchException: {e}")
        traceback.print_exc()
        # Test passes even on exception!
```
This test will pass whether it succeeds, fails, or throws an exception. It provides no value as a regression test.

**metasearch_test.py:25-37** - Same issue:
```python
def test_metasearch():
    try:
        query = "Mickey Mouse"
        text = metasearch(query, do_summarize=False)
        aprint(text)
        assert "Mickey" in text
    except DuckDuckGoSearchException as e:
        aprint(f"DuckDuckGoSearchException: {e}")
        traceback.print_exc()
        # Exception swallowed, test passes anyway
```

### 7.3 Missing Tests

1. **scrapper.py:**
   - `text_from_html()` with malformed HTML
   - `text_from_url()` with invalid URLs
   - `text_from_url()` with connection timeouts
   - `text_from_url()` with HTTP errors (404, 500)
   - Rate limiting behavior
   - `_tag_visible()` with various element types

2. **google.py:**
   - `_req()` with timeout
   - `search_google()` with no results
   - `search_google()` with malformed HTML response
   - `SearchResult` class
   - URL encoding edge cases

3. **duckduckgo.py:**
   - `search_images_ddg()` (no tests at all)
   - `install_latest_ddg()` (no tests)
   - Empty results handling
   - Invalid language codes

4. **wikipedia.py:**
   - No results found
   - Very long text truncation

5. **metasearch.py:**
   - Partial failures (one engine fails, other succeeds)

---

## 8. Recommendations Summary

### Critical Priority
1. **Fix rate limiting bug** in `scrapper.py:106-112` - update `_last_query_time_ms` after each query
2. **Fix mutable dict modification** in `google.py:31-32` - use `.copy()`
3. **Add URL validation** in `scrapper.py` to prevent SSRF
4. **Fix tests that silently pass on exception** in `google_test.py` and `metasearch_test.py`

### High Priority
1. **Add timeout to HTTP requests** in `scrapper.py:91`
2. **Add HTTP error handling** with appropriate exceptions
3. **Fix return type annotations** in `duckduckgo.py:42-43` and `google.py:73-80`
4. **Add maximum iteration guard** in `google.py:87` to prevent infinite loops

### Medium Priority
1. **Add comprehensive type annotations** throughout the package
2. **Add docstrings** to all public functions
3. **Create common search engine interface** (Protocol)
4. **Add unit tests with mocked HTTP** to avoid external dependencies
5. **URL-encode query parameters** properly in `google.py:66`
6. **Rename `scrapper.py` to `scraper.py`** (correct spelling)

### Low Priority
1. **Update User-Agent strings** to more recent browser versions
2. **Add module-level docstrings** explaining purpose
3. **Move imports to top of file** in `google.py`
4. **Fix misleading comments** in `wikipedia.py` and `google.py`
5. **Consolidate logging approach** (currently uses `arbol`)

---

## 9. Files Reviewed

| File | Lines | Status |
|------|-------|--------|
| `__init__.py` | 1 | Empty - OK |
| `headers.py` | 11 | Needs updates |
| `scrapper.py` | 114 | Multiple issues |
| `google.py` | 108 | Multiple issues |
| `duckduckgo.py` | 87 | Needs type fixes |
| `wikipedia.py` | 33 | Minor issues |
| `metasearch.py` | 30 | Minor issues |
| `test/__init__.py` | 1 | Empty - OK |
| `test/scrapper_test.py` | 14 | Needs expansion |
| `test/google_test.py` | 19 | Silent failures |
| `test/duckduckgo_test.py` | 46 | Good structure |
| `test/wikipedia_test.py` | 72 | Good skip logic |
| `test/metasearch_test.py` | 38 | Silent failures |

**Total Lines of Code:** ~573 (excluding empty init files)
**Total Issues Found:** 47
- Critical: 0
- High: 7
- Medium: 24
- Low: 16
