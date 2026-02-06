# Test Review: utils/web

## Summary

The `utils/web/` package contains six source files and five test files. Every test in the suite makes live HTTP requests to external services (Google, DuckDuckGo, Wikipedia, image.sc forum) with no mocking whatsoever. This makes the entire test suite inherently flaky, non-deterministic, and unsuitable for CI. The `headers.py` module has no test file at all. Several public functions have zero test coverage. Assertions are generally weak -- most only check that a keyword appears somewhere in arbitrary web content. There is not a single unit test in the package that tests code logic in isolation.

**Source files reviewed:**
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/web/duckduckgo.py` (4 public functions)
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/web/google.py` (4 public functions/classes)
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/web/headers.py` (1 public constant)
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/web/metasearch.py` (1 public function)
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/web/scrapper.py` (4 public functions/helpers)
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/web/wikipedia.py` (1 public function)

**Test files reviewed:**
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/web/test/duckduckgo_test.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/web/test/google_test.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/web/test/metasearch_test.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/web/test/scrapper_test.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/web/test/wikipedia_test.py`

---

## Coverage Gaps

### Missing Test Files
| Source File | Test File | Status |
|---|---|---|
| `headers.py` | *(none)* | **No test file exists** |

### Untested Public Functions

| Source File | Function/Class | Tested? |
|---|---|---|
| `duckduckgo.py` | `summary_ddg()` | Yes (via `test_duckduckgo_search_overview_summary`, `test_duckduckgo_search_overview`) |
| `duckduckgo.py` | `search_ddg()` | **No** -- only tested indirectly through `summary_ddg()` |
| `duckduckgo.py` | `search_images_ddg()` | **No** -- completely untested |
| `duckduckgo.py` | `install_latest_ddg()` | **No** -- completely untested |
| `google.py` | `SearchResult` class | **No** -- never instantiated or tested |
| `google.py` | `search_google()` | **No** -- completely untested |
| `google.py` | `search_overview()` | Yes (via `test_google_search_overview`) |
| `google.py` | `_req()` | **No** -- not tested directly |
| `google.py` | `_get_useragent()` | **No** -- not tested directly |
| `scrapper.py` | `text_from_html()` | **No** -- only tested indirectly through `text_from_url()` |
| `scrapper.py` | `text_from_url()` | Yes (via `test_scrapper`) |
| `scrapper.py` | `_tag_visible()` | **No** -- not tested directly |
| `metasearch.py` | `metasearch()` | Yes |
| `wikipedia.py` | `search_wikipedia()` | Yes |
| `headers.py` | `_scrapping_request_headers` | **No** -- no test file |

**Summary:** Out of approximately 12 public/semi-public symbols across six source files, only 5 are directly tested. At least 7 public functions/classes have zero direct test coverage.

---

## Weak Tests

### 1. `google_test.py::test_google_search_overview` -- No assertions at all

```python
def test_google_search_overview():
    try:
        term = "wiki Mickey Mouse"
        text = search_overview(term)
        aprint(text)
    except DuckDuckGoSearchException as e:
        aprint(f"DuckDuckGoSearchException: {e}")
        traceback.print_exc()
```

**Problems:**
- There is **zero assertion** in this test. It can never fail (except from an unhandled exception). It is functionally a no-op.
- The exception handler catches `DuckDuckGoSearchException` but this is a Google search test. The wrong exception type is caught -- `search_overview` calls `text_from_url` via `requests.get()`, which would raise `requests.exceptions.RequestException`, not `DuckDuckGoSearchException`.
- The exception is silently swallowed with `aprint` and `traceback.print_exc()` instead of failing or skipping the test.
- This test provides **zero signal** about whether the code works correctly.

### 2. `scrapper_test.py::test_scrapper` -- Minimal assertion

```python
def test_scrapper():
    url = "https://forum.image.sc/t/image-registration-in-python/51743"
    text = text_from_url(url)
    aprint(text)
    assert len(text) > 0
```

**Problems:**
- Asserts only that the result is non-empty. An error page, a redirect, or garbage HTML would all pass.
- No test of `text_from_html()` directly, which is the core parsing logic.
- No test of cleanup parameters (`cleanup`, `max_text_snippets`, `min_words_per_snippet`, `sort_snippets_by_decreasing_size`).
- Makes a real HTTP request to `forum.image.sc`, which could be down or rate-limited.
- No skip condition or exception handling for network failures.

### 3. `duckduckgo_test.py` -- Both tests test the same function with the same query

Both `test_duckduckgo_search_overview_summary` and `test_duckduckgo_search_overview` call `summary_ddg(query="Mickey Mouse")` and assert `"Mickey" in text`. The only difference is `do_summarize=True` vs `do_summarize=False`. They do not test `search_ddg()` or `search_images_ddg()` at all.

### 4. All assertions are keyword-presence checks

Every assertion across all test files follows the pattern `assert "SomeKeyword" in text`. This is extremely weak because:
- The keyword could appear in an error message, disclaimer, or unrelated content.
- It says nothing about the structure or quality of the returned data.
- It is non-deterministic -- web content changes over time.

---

## Missing Corner Cases

### `duckduckgo.py`
- **Empty query**: What happens when `query=""` is passed to `search_ddg()`?
- **`num_results=0`**: Does it handle zero requested results?
- **Non-English language**: The `lang` parameter conversion (`"en"` -> `"en-us"`) is tested implicitly but never verified directly.
- **`search_ddg()` returning `None`**: Line 50-53 checks `if results:` but this is never tested.
- **`summary_ddg()` exception path**: The broad `except Exception` on line 36 returns a failure string. This path is never tested.
- **`search_images_ddg()`**: Completely untested -- zero coverage.

### `google.py`
- **`search_google()` generator**: The main search function is a generator that yields results. It is completely untested.
- **`SearchResult` class**: Never instantiated in tests. `__repr__` never verified.
- **HTTP error responses**: `_req()` calls `resp.raise_for_status()` but no test verifies exception behavior on 4xx/5xx.
- **Pagination logic**: `search_google()` has a `while start < num_results` loop with pagination. Never tested.
- **`sleep_interval` parameter**: Never tested.
- **`advanced=True` vs `advanced=False`**: Different return types (SearchResult vs URL string) -- never tested.

### `scrapper.py`
- **`text_from_html()` with various HTML structures**: Never tested with crafted HTML. This is the function most amenable to pure unit testing.
- **`_tag_visible()` filtering**: Never tested with script tags, style tags, comments, meta tags.
- **`cleanup=False` path**: Never tested.
- **`max_text_snippets` parameter**: Never tested.
- **`min_words` filtering**: Never tested.
- **`sort_snippets_by_decreasing_size=False`**: Never tested.
- **Rate limiting logic in `text_from_url()`**: The `max_query_freq_hz` rate limiter using global `_last_query_time_ms` is never tested.
- **Empty HTML**: What happens with `text_from_html("")`?
- **HTTP timeout or connection errors**: Never tested.

### `metasearch.py`
- **Failure of one search engine**: If Google fails but DuckDuckGo succeeds (or vice versa), what happens? Never tested.
- **Both search engines returning empty results**: Never tested.

### `wikipedia.py`
- **No Wikipedia results found**: When `search_ddg()` returns an empty list, `text` becomes `""`. This path is not explicitly tested.
- **`max_text_length` truncation**: Never verified that truncation actually happens at the right boundary.
- **`llm` parameter passthrough**: Never tested with a mock LLM.
- **`num_results` greater than 10**: The `min(10, num_results)` clamping is never tested.

### `headers.py`
- **No tests exist at all**: While this is just a constant dictionary, a simple structural test (e.g., verifying required keys are present) would catch accidental modifications.

---

## Redundant Tests

### `duckduckgo_test.py`: Partially redundant pair
`test_duckduckgo_search_overview_summary` and `test_duckduckgo_search_overview` are nearly identical. They call the same function with the same query and differ only in `do_summarize`. While testing both code paths is reasonable, both tests make live DuckDuckGo API calls. The non-summarized variant (`do_summarize=False`) could be tested by mocking the DDGS call and verifying the text assembly logic, making the tests independent and faster.

### `wikipedia_test.py`: Three tests with the same structure
All three tests (`test_wikipedia_search_MM`, `test_wikipedia_search_AE`, `test_wikipedia_search_CZB`) follow the exact same pattern: search for a term, check if the term appears in the result. The value of testing three different search terms against a live API is minimal -- if one works, they all likely work. Two of the three could be replaced with parameterized tests or removed entirely. The structural variety (e.g., testing `do_summarize=True` vs `False`, testing `max_text_length`, testing `num_results`) would be more valuable than testing multiple queries.

---

## Positive Findings

1. **Skip conditions for LLM-dependent tests**: Tests that require an LLM (for summarization) properly use `@pytest.mark.skipif(not is_llm_available(), ...)`. This is a good practice that prevents CI failures when API keys are absent.

2. **DuckDuckGo exception handling**: The duckduckgo, metasearch, and wikipedia test files all catch `DuckDuckGoSearchException` and call `pytest.skip()`, acknowledging the flaky nature of external API tests.

3. **GitHub Actions skip**: `wikipedia_test.py` uses `IN_GITHUB_ACTIONS` to skip tests that are known to be unreliable in CI, which is pragmatic.

4. **Rate-limit awareness**: The duckduckgo tests check for `"Web search failed"` in the result text and skip accordingly, which prevents false failures due to rate limiting.

5. **Test file organization**: Test files follow a consistent naming convention (`<module>_test.py`) and are placed in a dedicated `test/` subdirectory with an `__init__.py`.

---

## Detailed Analysis per File

### 1. `duckduckgo.py` / `duckduckgo_test.py`

**Source analysis:**
- `summary_ddg()`: Calls `search_ddg()`, formats results, optionally summarizes with LLM. Has a broad `except Exception` fallback.
- `search_ddg()`: Wraps `DDGS().text()`. Converts `"en"` to `"en-us"`. Returns list of dicts.
- `search_images_ddg()`: Wraps `DDGS().images()`. Returns list of dicts. Similar structure to `search_ddg()`.
- `install_latest_ddg()`: Utility to upgrade the duckduckgo_search package.

**Test analysis:**
- `test_duckduckgo_search_overview_summary()`: Tests `summary_ddg(do_summarize=True)`. Requires LLM. Skips if rate-limited. Asserts `"Mickey" in text`.
- `test_duckduckgo_search_overview()`: Tests `summary_ddg(do_summarize=False)`. No LLM required. Same query and assertion.

**Gaps:**
- `search_ddg()` is never tested directly. Its return type (list of dicts with keys `title`, `body`, `href`) is never verified.
- `search_images_ddg()` has zero test coverage.
- `install_latest_ddg()` has zero test coverage (though this is more of an operational function).
- No mocking of `DDGS()` -- every test hits the live API.
- The exception handling path in `summary_ddg()` (line 36-38) is never tested.
- The `num_results` and `lang` parameters are never varied in tests.

**Recommendations:**
- Add a unit test for `search_ddg()` with a mocked `DDGS` instance to verify the return structure.
- Add at least one test for `search_images_ddg()`.
- Add a test that mocks `DDGS().text()` to return `None` or an empty list to test the empty-results branch.
- Add a test that mocks `DDGS().text()` to raise an exception to verify `summary_ddg()` returns the failure message.

---

### 2. `google.py` / `google_test.py`

**Source analysis:**
- `_get_useragent()`: Returns a random user agent string from a hardcoded list.
- `_req()`: Makes an HTTP GET to Google search. Uses `_scrapping_request_headers`. Calls `raise_for_status()`.
- `SearchResult`: Simple data class with `url`, `title`, `description` fields and `__repr__`.
- `search_overview()`: Builds a Google search URL, delegates to `text_from_url()` from scrapper.
- `search_google()`: Generator that paginates through Google results, parses HTML, yields `SearchResult` or URL strings.

**Test analysis:**
- `test_google_search_overview()`: Calls `search_overview("wiki Mickey Mouse")` and prints the result. **Has no assertions.** Catches `DuckDuckGoSearchException` (wrong exception type for a Google search). Silently swallows errors.

**Gaps (critical):**
- The test has **zero assertions** -- it literally cannot fail from a correctness standpoint.
- `search_google()`, the primary search function, is completely untested.
- `SearchResult` class is untested.
- `_req()` is untested.
- `_get_useragent()` is untested (though it is trivial).
- The exception type caught (`DuckDuckGoSearchException`) is incorrect for the function being tested.
- No mocking at all.

**Recommendations:**
- At minimum, add `assert len(text) > 0` to the existing test, plus a skip condition for network failures.
- Fix the exception type to `requests.exceptions.RequestException` or a generic `Exception`.
- Add a unit test for `search_google()` with mocked HTTP responses using crafted Google-like HTML.
- Add a unit test for `SearchResult.__repr__()`.
- Consider testing `_get_useragent()` returns a string from the list.

---

### 3. `headers.py` -- No test file

**Source analysis:**
- Contains a single module-level constant `_scrapping_request_headers` -- a dict of HTTP headers used for web scraping.

**Gaps:**
- No test file exists.
- While this is just a constant, it is imported by both `google.py` and `scrapper.py`. A structural test verifying that expected keys (`User-Agent`, `Accept`, `Accept-Language`, etc.) are present would catch accidental breakage.

**Recommendations:**
- Add a minimal test that verifies the dict has the expected keys and non-empty values.

---

### 4. `scrapper.py` / `scrapper_test.py`

**Source analysis:**
- `_tag_visible()`: Filter function for BeautifulSoup -- hides script, style, head, title, meta, comments.
- `text_from_html()`: Core HTML-to-text extraction. Has parameters for cleanup, snippet limits, minimum word count, sorting.
- `_current_time_ms()`: Returns current time in milliseconds.
- `text_from_url()`: Fetches URL content, calls `text_from_html()`, implements rate limiting via global state.

**Test analysis:**
- `test_scrapper()`: Fetches a real URL (`https://forum.image.sc/t/image-registration-in-python/51743`), asserts `len(text) > 0`.

**Gaps (critical):**
- `text_from_html()` is the most testable function in the entire package -- it takes raw HTML and returns text. It should have extensive unit tests with crafted HTML inputs. It has **zero direct tests**.
- `_tag_visible()` is never tested with different element types.
- None of the `text_from_html()` parameters are tested:
  - `cleanup=True` vs `cleanup=False`
  - `max_text_snippets` limiting
  - `min_words` filtering
  - `sort_snippets_by_decreasing_size` ordering
- The rate limiting logic in `text_from_url()` is never tested.
- No test for HTTP failures (connection errors, timeouts, 404s, 500s).
- No test for malformed HTML input.
- The single test makes a live HTTP request with no skip condition for network failure.

**Recommendations:**
- Add pure unit tests for `text_from_html()` with crafted HTML strings. For example:
  - HTML with `<script>` and `<style>` tags (should be filtered out)
  - HTML with comments (should be filtered out)
  - HTML with short text snippets below `min_words` threshold
  - Test `max_text_snippets` limits the output
  - Test `sort_snippets_by_decreasing_size` ordering
  - Test `cleanup=False` preserves whitespace
- Add a unit test for `_tag_visible()` with mock elements.
- Mock `Session.get()` in `text_from_url()` tests to test rate limiting behavior.
- Add a network failure skip condition to the existing integration test.

---

### 5. `metasearch.py` / `metasearch_test.py`

**Source analysis:**
- `metasearch()`: Combines `search_overview()` (Google) and `summary_ddg()` (DuckDuckGo), optionally summarizes with LLM.

**Test analysis:**
- `test_metasearch_summary()`: Tests with `do_summarize=True`. Requires LLM. Asserts `"Mickey" in text`.
- `test_metasearch()`: Tests with `do_summarize=False`. Asserts `"Mickey" in text`.

**Gaps:**
- Both tests hit live Google and DuckDuckGo APIs simultaneously.
- No test for when one search engine fails and the other succeeds.
- No test for when both return empty results.
- No mocking -- this is purely an integration test.
- The `num_results` and `lang` parameters are never varied.

**Recommendations:**
- Add unit tests with mocked `search_overview()` and `summary_ddg()` to test the combination logic.
- Test the case where one search engine fails (returns error/empty).
- Parameterize existing integration tests or mark them explicitly as integration tests.

---

### 6. `wikipedia.py` / `wikipedia_test.py`

**Source analysis:**
- `search_wikipedia()`: Calls `search_ddg()` with `site:wikipedia.org` appended to query, joins `body` fields, truncates to `max_text_length`, optionally summarizes.

**Test analysis:**
- `test_wikipedia_search_MM()`: Tests with `do_summarize=False` for "Mickey Mouse". Skips in GitHub Actions.
- `test_wikipedia_search_AE()`: Tests with `do_summarize=True` for "Albert Einstein". Requires LLM. Skips in GitHub Actions.
- `test_wikipedia_search_CZB()`: Tests with `do_summarize=True` for "CZ Biohub". Requires LLM. Skips in GitHub Actions.

**Gaps:**
- Three tests with nearly identical structure but different query strings. Two of the three are redundant.
- `max_text_length` truncation is never verified.
- `num_results` parameter behavior is never tested.
- The `min(10, num_results)` clamping logic is never tested.
- The `llm` parameter passthrough is never tested.
- Empty results from `search_ddg()` are never tested (would produce `""` from `"\n\n".join([])`).
- No mocking of `search_ddg()`.

**Recommendations:**
- Add a unit test with mocked `search_ddg()` returning known results to verify text assembly and truncation.
- Test `max_text_length` with a result that exceeds the limit.
- Test `num_results > 10` to verify the `min()` clamping.
- Test empty results list.
- Consolidate the three integration tests into one or use `pytest.mark.parametrize`.

---

## Cross-Cutting Issues

### 1. No Mocking Anywhere
Not a single test in the entire `utils/web/test/` directory uses `unittest.mock`, `pytest-mock`, `responses`, `requests-mock`, or any other mocking library. Every test makes live HTTP requests. This is the single biggest issue with the test suite.

### 2. Tests Are Integration Tests, Not Unit Tests
All tests are end-to-end integration tests that depend on external services. They should be either:
- Refactored into unit tests with mocked network calls, OR
- Explicitly marked as integration tests (e.g., `@pytest.mark.integration`) and excluded from default CI runs.

### 3. Global Mutable State in `scrapper.py`
The `_last_query_time_ms` global variable in `scrapper.py` (line 78) creates hidden coupling between tests. If tests run in a certain order, the rate limiter could cause unexpected delays or behavior. This is never tested.

### 4. Inconsistent Exception Handling in Tests
- `google_test.py` catches `DuckDuckGoSearchException` for a Google search (wrong exception type) and silently swallows it.
- `duckduckgo_test.py` catches `DuckDuckGoSearchException` and calls `pytest.skip()` (correct).
- `scrapper_test.py` has no exception handling at all (will fail on network error).
- `wikipedia_test.py` and `metasearch_test.py` catch `DuckDuckGoSearchException` and skip (correct).

### 5. `aprint()` Used for Debugging, Not Assertions
Nearly every test calls `aprint(text)` to print results. This is debugging output, not a meaningful test action. It clutters test output and provides no signal about correctness.

### 6. Return Type Annotation Bug in `search_ddg()`
The function signature says `-> str` but it actually returns `list[dict]`. This is a source code bug, not a test bug, but a test verifying the return type would have caught it.
