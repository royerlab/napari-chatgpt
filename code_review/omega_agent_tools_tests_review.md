# Test Review: omega_agent/tools

## Summary

The `omega_agent/tools/` package contains **26 source files** across four subpackages (`base`, `special/`, `search/`, `napari/` including `napari/delegated_code/`). Of these, only **10 have any test coverage at all**, and the quality of coverage is generally shallow. The majority of tests fall into three categories: (1) integration/smoke tests that call real external services, (2) source-code inspection tests that grep the source text for specific strings rather than testing behavior, and (3) import-existence tests that merely verify a module or function can be imported. None of the tool base classes (`BaseOmegaTool`, `BaseNapariTool`) have any unit tests. Mocking is essentially absent throughout the test suite -- external dependencies like DuckDuckGo search, web scraping, and LLM APIs are called directly, making the tests slow, flaky, and environment-dependent.

**Key statistics:**
- Source files with tests: 10 out of 26 (38%)
- Source files with NO tests: 16 (62%)
- Tests using mocks: 0
- Tests verifying error/edge cases: 0
- Tests inspecting source code text rather than behavior: 3 files (file_open_tool_test, image_denoising_tool_test, stardist_imports_test)

---

## Coverage Gaps (source files with NO tests)

The following 16 source files have **zero test coverage**:

### Base and Infrastructure
| File | Description | Risk |
|------|-------------|------|
| `base_omega_tool.py` | Abstract base class for all Omega tools; `normalise_to_string()`, `pretty_string()` logic | **HIGH** -- foundational class, every tool depends on it |
| `base_napari_tool.py` | Complex base class with `_prepare_code()`, `_run_code_catch_errors_fix_and_try_again()`, queue-based napari communication, LLM delegation | **CRITICAL** -- the most complex class in the package, ~350 lines of untested code |
| `omega_tool_callbacks.py` | `OmegaToolCallbacks` -- dispatches lifecycle events (start, activity, end, error) | **MEDIUM** -- simple delegation but used everywhere |
| `generic_coding_instructions.py` | Template string for code generation prompts | LOW -- data-only module |

### Special Tools (all untested)
| File | Description | Risk |
|------|-------------|------|
| `special/exception_catcher_tool.py` | Catches uncaught exceptions via `sys.excepthook`; queue-based exception reporting | **HIGH** -- modifies global `sys.excepthook` at import time |
| `special/file_download_tool.py` | Downloads files from URLs extracted from queries | MEDIUM |
| `special/human_input_tool.py` | Prompts user for input; uses `pydantic.Field` for callable defaults | LOW (interactive) |
| `special/package_info_tool.py` | Lists/filters installed Python packages | MEDIUM |
| `special/pip_install_tool.py` | Installs pip packages based on comma-separated input | **HIGH** -- system-modifying tool |
| `special/python_repl.py` | Executes arbitrary Python via `exec()`/`eval()`; has `sanitize_input()` | **HIGH** -- security-sensitive |

### Napari Tools (all untested)
| File | Description | Risk |
|------|-------------|------|
| `napari/cell_nuclei_segmentation_tool.py` | Orchestrates segmentation (cellpose/stardist/classic); dynamic code loading | **HIGH** |
| `napari/viewer_control_tool.py` | LLM-generated code to control napari viewer | **HIGH** |
| `napari/viewer_execution_tool.py` | LLM-generated arbitrary code execution against napari | **HIGH** |
| `napari/viewer_query_tool.py` | LLM-generated code to query napari state | **HIGH** |
| `napari/viewer_vision_tool.py` | Uses vision LLM to describe layer images; complex regex parsing | **HIGH** |
| `napari/widget_maker_tool.py` | Generates magicgui widgets from LLM code; dynamic import + viewer docking | **HIGH** |

### Delegated Code
| File | Description | Risk |
|------|-------------|------|
| `napari/delegated_code/signatures.py` | String constants for function signatures | LOW -- data-only |

---

## Weak Tests

### 1. `tests/functions_info_tests.py` -- Fragile assertions on response length

**File:** `src/napari_chatgpt/omega_agent/tools/tests/functions_info_tests.py`

```python
def test_tools():
    tool = PythonFunctionsInfoTool()
    query = "skimage.morphology.watershed"
    result = tool.run_omega_tool(query)
    assert len(result) < 300
    assert "markers = None" in result
```

**Issues:**
- The `assert len(result) < 300` is extremely fragile. If `skimage` updates its docstrings, this test breaks.
- The test relies on the exact text `"markers = None"` being present in the function signature. This is version-dependent.
- When the result exceeds 512 characters, the code calls `summarize()` which invokes an LLM. This means the test could silently trigger an LLM API call depending on the version of scikit-image installed.
- No test for the error path (invalid function name).
- No test for the `*` prefix (docstring mode) failing.
- Only one function is tested. The `extract_package_path()` edge cases are not covered.

### 2. `tests/web_search_tool_tests.py` -- Network-dependent, no mocking

**File:** `src/napari_chatgpt/omega_agent/tools/tests/web_search_tool_tests.py`

```python
def test_web_search_tool():
    tool = WebSearchTool()
    query = "What is zebrahub?"
    result = tool.run_omega_tool(query)
    pprint(result)
    assert "atlas" in result or "zebrafish" in result or "RNA" in result
```

**Issues:**
- Calls real DuckDuckGo/Google search APIs -- will fail offline, rate-limited, or if search results change.
- The assertion is a loose OR of three terms. This could pass even if the search returned garbage about zebrafish unrelated to Zebrahub.
- No exception handling around network failures (unlike the Wikipedia test which at least catches `DuckDuckGoSearchException`).
- No mock of `metasearch()` to test tool logic in isolation.
- No test for the error handling path (what happens when `metasearch()` raises?).

### 3. `tests/wikipedia_search_tool_tests.py` -- Better but still network-dependent

**File:** `src/napari_chatgpt/omega_agent/tools/tests/wikipedia_search_tool_tests.py`

**Issues:**
- At least handles `DuckDuckGoSearchException` with `pytest.skip`, which is better than the web search test.
- Still calls real external APIs; no mocking.
- The `pytest.skip` on empty results masks real failures.
- No test for error message formatting on exception.

### 4. `napari/delegated_code/test/cellpose_test.py` and `stardist_test.py` -- Heavy integration tests

**Files:**
- `src/napari_chatgpt/omega_agent/tools/napari/delegated_code/test/cellpose_test.py`
- `src/napari_chatgpt/omega_agent/tools/napari/delegated_code/test/stardist_test.py`

**Issues:**
- These test the *delegated code functions* (e.g., `cellpose_segmentation()`, `stardist_segmentation()`), not the tool classes themselves.
- They require cellpose/stardist to be installed (correctly skip if not).
- The label count assertions (`20 <= nb_unique_labels <= 30`) are reasonable but version-sensitive.
- They load `skimage.data.cells3d()` which downloads data on first use -- potential CI failure.
- The `show_viewer` parameter with `napari.run()` in the test body is a manual/interactive debugging aid and should not be in automated test code (though it is gated by `show_viewer=False`).
- No test for edge cases: empty images, 1D images, 4D+ images (which should raise `ValueError`), non-float input, etc.

### 5. `napari/delegated_code/test/classic_test.py` -- Exact label count assertions

**File:** `src/napari_chatgpt/omega_agent/tools/napari/delegated_code/test/classic_test.py`

```python
assert nb_unique_labels == 21
```

**Issues:**
- Uses exact equality for label counts. This is fragile if scikit-image algorithms change behavior across versions.
- No `skipif` decorator -- will always run even if dependencies change.
- Same `show_viewer` pattern as above.
- Typo in function name: `test_classsic_2d` and `test_classsic_3d` (three 's'es).
- No test for different threshold types (only default `otsu` is tested).
- No test for `apply_watershed=True`.
- No test for invalid `threshold_type` (should raise `ValueError`).

### 6. `napari/delegated_code/test/stardist_imports_test.py` -- Import smoke tests

**File:** `src/napari_chatgpt/omega_agent/tools/napari/delegated_code/test/stardist_imports_test.py`

**Issues:**
- All five tests just verify that modules/functions can be imported and are callable/not-None.
- `test_any_type_is_available_in_stardist_module` inspects source code text for `"Any"` -- this is a source-text test, not a behavioral test. If the type annotation changes (e.g., to `object`), the test logic is flawed.
- These tests were clearly written to verify a specific bug fix (missing `Any` import). While regression tests are valuable, they should test the *behavior* (e.g., calling the function with `model=None` should work) rather than grepping source code.

### 7. `napari/test/file_open_tool_test.py` -- Source text inspection, not behavior

**File:** `src/napari_chatgpt/omega_agent/tools/napari/test/file_open_tool_test.py`

```python
def test_file_open_tool_error_message_no_double_negative():
    source = inspect.getsource(NapariFileOpenTool)
    assert "could not be opened" not in source
    assert "could be opened" in source
```

**Issues:**
- This tests the *text* of the source code, not the *behavior* of the tool.
- If someone refactors the error message to say "failed to open" (semantically correct, no double negative), this test would fail.
- A proper test would mock `open_in_napari()` to return `False` and verify the returned message string.
- The other two tests (`test_file_open_tool_module_imports`, `test_napari_file_open_tool_class_exists`) are pure import tests with zero behavioral verification.

### 8. `napari/test/image_denoising_tool_test.py` -- Source text inspection, not behavior

**File:** `src/napari_chatgpt/omega_agent/tools/napari/test/image_denoising_tool_test.py`

```python
def test_image_denoising_uses_platform_machine():
    source = inspect.getsource(install_aydin)
    assert "sys.platform.uname()" not in source
    assert "platform.machine()" in source
```

**Issues:**
- Same pattern as file_open_tool_test: inspects source code text.
- A proper test would mock `platform.machine()` to return `"arm64"` and `platform.system()` to return `"Darwin"` and verify that `NotImplementedError` is raised.
- The remaining tests are pure import/existence checks.

---

## Missing Corner Cases

### BaseOmegaTool (no tests at all)
- `normalise_to_string()`: no test for dict input, list input, singleton list, non-string values
- `pretty_string()`: no test for descriptions shorter than 80 characters, descriptions with no period after character 80, empty descriptions

### BaseNapariTool (no tests at all)
- `run_omega_tool()`: no test for the case where `self.prompt` is None (no LLM delegation)
- `run_omega_tool()`: no test for `ExceptionGuard` response from napari queue
- `_prepare_code()`: no test for markdown extraction, import fixing, bad call fixing, missing package installation, line filtering
- `_run_code_catch_errors_fix_and_try_again()`: no test for retry logic, decreasing `nb_tries`, final exception raising

### PythonFunctionsInfoTool
- No test for non-existent function path
- No test for function with very short info (<= 512 chars, no summarization)
- No test for exception in `get_function_info()`
- No test for query with no qualified function name

### WebImageSearchTool (no tests at all)
- `_run_code()`: no test for parsing integer from parentheses
- No test for zero search results
- No test for all downloads failing
- No test for `nb_images` exceeding available URLs

### ExceptionCatcherTool (no tests at all)
- No test for non-integer input
- No test for empty exception queue
- No test for multiple exceptions in queue

### PythonCodeExecutionTool (no tests at all)
- `sanitize_input()`: no test for backtick removal, "python" prefix removal
- No test for multi-statement code
- No test for code with side effects
- No test for syntax errors in input

### CellNucleiSegmentationTool
- No test for the code-routing logic (cellpose vs stardist vs classic detection in generated code)
- No test for `ValueError` when segmentation function cannot be determined

### Classic segmentation
- No test for `apply_watershed=True`
- No test for invalid `threshold_type`
- No test for images with uniform values (threshold algorithms may fail)
- No test for 1D or 4D+ images

### Cellpose/Stardist segmentation
- No test for `ValueError` on 4D+ images
- No test for different `model_type` values
- No test for `normalize=False`
- No test for custom `channel` or `diameter` parameters

### ViewerVisionTool (no tests at all)
- Complex regex parsing for layer names (`*layer_name*` syntax) -- completely untested
- Fallback logic for selected/active/current layers -- untested
- Edge case: match with only one `*` -- untested

---

## Redundant Tests

### stardist_imports_test.py overlaps with stardist_test.py
- `test_stardist_module_imports_without_error`, `test_stardist_segmentation_function_exists`, `test_stardist_2d_function_exists`, `test_stardist_3d_function_exists` are all strictly weaker than the tests in `stardist_test.py` which actually *call* these functions. If `stardist_test.py` passes, all import tests in `stardist_imports_test.py` are redundant.
- **Exception:** The `test_any_type_is_available_in_stardist_module` test is unique but tests source text, not behavior.

### utils_test.py partially overlaps with cellpose_test.py and stardist_test.py
- `test_check_stardist_actually_checks_import` and `test_check_cellpose_actually_checks_import` verify the same logic that the `@pytest.mark.skipif` decorators in cellpose_test.py and stardist_test.py rely on. These are not strictly redundant but provide little additional value if the integration tests run.

### file_open_tool_test.py and image_denoising_tool_test.py
- `test_file_open_tool_module_imports` / `test_napari_file_open_tool_class_exists` and `test_image_denoising_tool_module_imports` / `test_install_aydin_function_exists` are pure existence checks that provide zero behavioral coverage. Any test that actually *uses* the class would subsume these.

---

## Positive Findings

1. **utils_test.py is the strongest test file.** It verifies that `check_stardist_installed()` and `check_cellpose_installed()` *actually check imports* rather than returning `True` unconditionally (regression test for a real bug). It cross-references the function result against an independent import check. It also tests `get_list_of_algorithms()` and `get_description_of_algorithms()` for correct return types and expected content.

2. **Proper use of `pytest.mark.skipif` in cellpose_test.py and stardist_test.py.** Tests correctly skip when optional heavy dependencies (cellpose, stardist) are not installed, avoiding false failures in CI environments without GPU or ML libraries.

3. **wikipedia_search_tool_tests.py handles external flakiness.** The test catches `DuckDuckGoSearchException` and uses `pytest.skip()`, acknowledging that external search services may be unavailable. This is a reasonable pattern for integration tests.

4. **Cellpose and stardist tests provide genuine integration coverage.** Despite being slow and dependency-heavy, these tests exercise the complete segmentation pipeline (2D and 3D) and verify that the output has a reasonable number of labels. The relaxed range assertions (e.g., `20 <= nb_unique_labels <= 30`) are a pragmatic approach to version sensitivity.

5. **classic_test.py tests both 2D and 3D paths.** The two tests cover the dimensionality branching in `classic_segmentation()`.

6. **Regression tests exist for known bugs.** The stardist_imports_test (missing `Any` import), file_open_tool_test (double negative), and image_denoising_tool_test (`sys.platform.uname()` bug) all document and guard against specific historical bugs, even if their testing methodology (source inspection) is suboptimal.

---

## Detailed Analysis per File

### `tests/functions_info_tests.py`
- **What it tests:** `PythonFunctionsInfoTool.run_omega_tool()` with two queries (one without `*`, one with `*` for docstrings).
- **Quality:** Moderate. Tests real behavior but with fragile assertions on string content and length.
- **Missing:** Error paths, invalid inputs, summarization path (LLM-dependent), edge cases.
- **Mocking:** None. May trigger real LLM calls via `summarize()`.

### `tests/web_search_tool_tests.py`
- **What it tests:** `WebSearchTool.run_omega_tool()` with a single query.
- **Quality:** Weak. Network-dependent, no error handling, loose assertion.
- **Missing:** Error path, empty results, network failures, mocking of `metasearch()`.
- **Mocking:** None.

### `tests/wikipedia_search_tool_tests.py`
- **What it tests:** `WikipediaSearchTool.run_omega_tool()` with "Albert Einstein".
- **Quality:** Moderate. Handles external failures gracefully with `pytest.skip`.
- **Missing:** Error message formatting, empty query, non-English results.
- **Mocking:** None.

### `napari/delegated_code/test/cellpose_test.py`
- **What it tests:** `cellpose_segmentation()` on 2D and 3D data from `skimage.data.cells3d()`.
- **Quality:** Good integration test. Properly skips if cellpose not installed. Range-based assertions.
- **Missing:** Edge cases (empty image, 4D, non-float, custom parameters). Does not test the `CellNucleiSegmentationTool` class itself.
- **Mocking:** None (deliberately -- this is an integration test).

### `napari/delegated_code/test/classic_test.py`
- **What it tests:** `classic_segmentation()` on 2D (max projection) and 3D data.
- **Quality:** Moderate. Exact label count assertions are fragile.
- **Missing:** Different threshold types, `apply_watershed=True`, invalid inputs, error paths. Typo in function names (`classsic`).
- **Mocking:** None.

### `napari/delegated_code/test/stardist_test.py`
- **What it tests:** `stardist_segmentation()` on 2D and 3D data.
- **Quality:** Good integration test. Properly skips, range-based assertions.
- **Missing:** Same as cellpose -- no edge cases, no tool-level testing.
- **Mocking:** None.

### `napari/delegated_code/test/stardist_imports_test.py`
- **What it tests:** Module importability and function existence for stardist module.
- **Quality:** Weak. All tests are import/existence checks or source-code inspection. Regression value only.
- **Missing:** Behavioral tests for the functions under test.
- **Mocking:** None.

### `napari/delegated_code/test/utils_test.py`
- **What it tests:** `check_stardist_installed()`, `check_cellpose_installed()`, `get_list_of_algorithms()`, `get_description_of_algorithms()`.
- **Quality:** Good. Cross-references function output against independent import checks. Verifies return types and content.
- **Missing:** What happens if one function raises an unexpected exception during import (e.g., `ImportError` from a transitive dependency).
- **Mocking:** None, but the design makes mocking unnecessary for the install-check tests.

### `napari/test/file_open_tool_test.py`
- **What it tests:** Source code text of `NapariFileOpenTool` for double-negative bug fix. Module importability.
- **Quality:** Weak. Source-code inspection is brittle. No behavioral testing of `_run_code()`.
- **Missing:** Actual file opening behavior (would need mocking of `open_in_napari` and a `Viewer` mock). Error message verification by calling the tool. Multiple files, plugin specification, error handling.
- **Mocking:** None.

### `napari/test/image_denoising_tool_test.py`
- **What it tests:** Source code text of `install_aydin()` for `platform.machine()` bug fix. Module importability.
- **Quality:** Weak. Source-code inspection only.
- **Missing:** Actual `install_aydin()` behavior on different platforms (mock `platform.system()` and `platform.machine()`). `ImageDenoisingTool._run_code()` is completely untested.
- **Mocking:** None.

---

## Recommendations (Priority Order)

1. **Add unit tests for `BaseNapariTool._prepare_code()`** -- This is the most complex untested method. It can be tested with mocked LLM and straightforward string inputs.

2. **Add unit tests for `BaseOmegaTool.normalise_to_string()` and `pretty_string()`** -- Pure functions, easy to test, foundational.

3. **Replace source-code inspection tests with behavioral tests** in `file_open_tool_test.py` and `image_denoising_tool_test.py`. Mock the external dependencies and verify actual return values.

4. **Add mocking to search tool tests** -- Mock `metasearch()` and `search_wikipedia()` to test tool logic without network calls. Keep the existing integration tests but mark them with `@pytest.mark.integration` or similar.

5. **Add edge-case tests for `classic_segmentation()`** -- Invalid `threshold_type`, `apply_watershed=True`, uniform-value images, different dimensionalities.

6. **Add tests for `PythonCodeExecutionTool.sanitize_input()`** -- This is a pure function with no dependencies, trivial to test, and security-relevant.

7. **Add tests for `ExceptionCatcherTool`** -- Mock the exception queue and verify output formatting.

8. **Add tests for `OmegaToolCallbacks`** -- Verify that the correct internal callables are dispatched.

9. **Fix the typo in `classic_test.py`** -- `test_classsic_2d` and `test_classsic_3d` should be `test_classic_2d` and `test_classic_3d`.

10. **Add a `conftest.py` with shared fixtures** (e.g., a mock `Viewer`, a mock `LLM`, a mock `Queue`) to enable tool-level testing without real napari or LLM instances.
