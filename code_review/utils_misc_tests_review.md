# Test Review: utils (misc packages)

## Summary

This review covers 12 utility sub-packages under `src/napari_chatgpt/utils/`. Of these, **5 packages have no tests at all**, and the remaining 7 have tests that are generally shallow -- primarily smoke tests verifying that functions run without crashing, but lacking meaningful edge-case coverage, boundary testing, and proper isolation from external services.

| Package | Source functions | Test file exists | Functions tested | Verdict |
|---------|----------------|-----------------|-----------------|---------|
| `configuration/` | 7 methods | Yes | 3 of 7 | Partial |
| `images/` | 1 function | Yes | 1 of 1 | Weak |
| `napari/` | 6 functions across 3 files | 1 test file for 1 of 3 files | 1 of 6 | Major gaps |
| `network/` | 2 functions | Yes | 1 of 2 | Partial |
| `notebook/` | 12 methods | Yes (2 files) | 5 of 12 | Partial |
| `openai/` | 5 functions across 4 files | Yes (3 files) | 4 of 5 | Reasonable (but see details) |
| `llm/` | 3 functions across 2 files | Yes (2 files) | 3 of 3 | Reasonable (but integration-only) |
| `system/` | 4 functions across 3 files | Yes (1 file) | 1 of 4 | Major gaps |
| `segmentation/` | 6 functions across 2 files | No | 0 of 6 | **No tests** |
| `download/` | 2 functions | No (empty test dir) | 0 of 2 | **No tests** |
| `async_utils/` | 1 function + 1 class | No | 0 of 2 | **No tests** |
| `anthropic/` | 1 function | No | 0 of 1 | **No tests** |

---

## Coverage Gaps

### Entirely Untested Packages (no test file at all)

1. **`utils/segmentation/`** -- `labels_3d_merging.py` has 5 public functions (`segment_3d_from_segment_2d`, `segment_2d_z_slices`, `make_slice_labels_different`, `merge_2d_segments`, `remove_small_segments`) and `remove_small_segments.py` has 1 function. Only a demo file exists, but no unit tests. These contain non-trivial 3D label merging logic that is highly susceptible to off-by-one errors and boundary conditions.

2. **`utils/download/`** -- `download_files.py` has 2 public functions (`download_files`, `download_file_stealth`). The `test/` directory exists but contains only `__init__.py`. No test coverage at all. The `download_file_stealth` function also has a potential resource leak (file handle opened with `open()` on line 56 is not properly guarded if an exception occurs during iteration).

3. **`utils/async_utils/`** -- `run_async.py` has `run_async()` and the helper `_RunThread` class. No test directory or test file exists. The function has two distinct code paths (running loop present vs. absent) -- neither is tested.

4. **`utils/anthropic/`** -- `model_list.py` has `get_anthropic_model_list()` which returns a hardcoded list. No tests exist. While trivial, a simple test asserting the list is non-empty and contains expected model name patterns would help catch regressions when the list is updated.

### Partially Tested Packages (test file exists but significant gaps)

5. **`utils/napari/`** -- Three source files exist (`layer_snapshot.py`, `napari_viewer_info.py`, `open_in_napari.py`), but only `napari_viewer_info.py` has a test. Functions `capture_canvas_snapshot()` (from `layer_snapshot.py`) and `open_in_napari()`, `open_video_in_napari()`, `open_zarr_in_napari()` etc. (from `open_in_napari.py`) have zero test coverage.

6. **`utils/system/`** -- Three source files (`folders.py`, `information.py`, `is_apple_silicon.py`), but only `information.py` is tested. `get_home_folder()`, `get_or_create_folder_in_home()` from `folders.py` and `is_apple_silicon()` from `is_apple_silicon.py` are untested.

7. **`utils/configuration/`** -- `AppConfiguration` has 7 methods (`__new__`, `__init__`, `load_default_config`, `load_configurations`, `save_configurations`, `get`, `__getitem__`, `__setitem__`). The test only exercises `__getitem__`, `__setitem__`, and the singleton pattern. The `get()` method (with default value auto-persistence), `load_default_config()` with a YAML file path, and `save_configurations()` called independently are untested.

8. **`utils/openai/`** -- `max_token_limit.py` has the `openai_max_token_limit()` function with **no test at all**. This is a purely deterministic function with multiple branches that could easily have unit tests.

---

## Weak Tests

### 1. `utils/images/test/normalize_test.py`
**File**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/images/test/normalize_test.py`

- **Single test case only**: Tests one input (10x10 arange) with `p_low=5, p_high=95, clip=True` (default). Never tests `clip=False`.
- **No edge cases**: Does not test constant images (where `v_high - v_low == 0`, which the source defends against with `+ 1e-6`), does not test negative values, float images, high-dimensional images, or the case where `p_low > p_high`.
- **Assertion is approximate but not rigorous**: The assertion checks `min()` and `max()` but does not verify intermediate values or the overall distribution shape.

### 2. `utils/napari/test/napari_viewer_info_test.py`
**File**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/napari/test/napari_viewer_info_test.py`

- **Single assertion**: `assert len(layers_info) > 0` is extremely weak. The test creates a comprehensive viewer with 7 different layer types, but only checks that the output string is non-empty.
- **No validation of content**: Does not check that layer names, types, shapes, or counts appear correctly in the output.
- **Untested helper functions**: `affine_to_single_line_string()`, `array_to_single_line_string()`, `layer_description()`, `get_viewer_state()`, `get_viewer_layers_info()` -- none have direct tests.
- **Does not test edge cases**: Empty viewer, viewer with only one layer, viewer with more than `max_layers` layers, layers without details (`max_layers_with_details=0`).

### 3. `utils/network/test/port_available_test.py`
**File**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/network/test/port_available_test.py`

- **`find_first_port_available()` is never tested**, despite having its own distinct logic (range iteration, return None case).
- **Misleading error message**: The test says "No port available between 5000 and 6000" but the search range is 9000-10000.
- **No assertion when no port found**: If `available_port is None`, the test silently passes without asserting anything -- effectively a no-op in that scenario.
- **Deprecation warning**: Uses `asyncio.get_event_loop()` which is deprecated in Python 3.10+; should use `asyncio.new_event_loop()`.

### 4. `utils/configuration/test/app_configuration_test.py`
**File**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/configuration/test/app_configuration_test.py`

- **No cleanup**: The test writes to `~/.test_app_configuration/config.yaml` but never cleans up, leaving persistent state on the filesystem. Repeated runs could have stale data from previous runs affecting results.
- **Singleton pattern partially tested**: The test verifies that `config_2` sees `config_1`'s changes, but since `__init__` is called every time (even for cached instances), the second instantiation reloads config and overwrites `self.config_data`. The test passes by coincidence -- the second `AppConfiguration("test_app_configuration")` actually re-reads the saved YAML. This means the test does not truly verify the singleton `__new__` behavior.
- **`get()` method untested**: The `get(key, default)` method has important auto-persistence logic (saves the default value when key is not found) that is never verified.
- **No test for YAML file default config**: `load_default_config()` with a string path is untested.

### 5. `utils/openai/test/check_api_key_test.py`
**File**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/openai/test/check_api_key_test.py`

- **Source-inspection tests are brittle**: Three tests use `inspect.getsource()` to check that certain strings appear or do not appear in the source code. These are code-style enforcement tests, not behavioral tests. They would break if the code were refactored to use different variable names.
- **`test_check_api_key_returns_bool` and `test_check_api_key_with_invalid_key_returns_false` make real API calls**: These tests actually call the OpenAI API with invalid keys, causing network requests. They should either be mocked or marked with a `skipif` for environments without network access.
- **No test for valid key scenario**: Only invalid keys are tested; the True return path is never verified (even via mocking).

### 6. `utils/openai/test/default_model_test.py` and `utils/openai/test/model_list_test.py`
**Files**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/openai/test/default_model_test.py`, `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/openai/test/model_list_test.py`

- Both are **integration tests** (require actual OpenAI API key), properly marked with `skipif`.
- **`test_model_list` is trivial**: Only asserts `len(model_list) > 0`, does not verify that filtered models actually match the `"gpt"` filter or that the exclusion list works.
- **`postprocess_openai_model_list()` in `model_list.py` is untested.** This is a purely deterministic function sorting/filtering models that could easily be unit-tested without any API access.
- **`test_default_model`**: Only asserts result starts with `"gpt-"`. Does not test the sorting logic in `model_key()` or the caching behavior (`_default_openai_model_name` global).

### 7. `utils/llm/test/summarizer_test.py` and `utils/llm/test/vision_test.py`
**Files**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/llm/test/summarizer_test.py`, `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/llm/test/vision_test.py`

- **Integration-only tests**: Both require a running LLM service. No unit tests with mocked LLMs exist.
- **`test_summarizer`**: Downloads from Wikipedia during test execution (flaky if network is down). The assertion `"Einstein" in summary or "physicist" in summary` is reasonable but fragile -- LLM outputs are non-deterministic.
- **`test_gpt_vision`**: Assertions on LLM-generated descriptions are inherently fragile. The test for `future.jpeg` has very specific expected terms that may not always appear.
- **`summarize()` empty-string path untested**: The early return for empty text after `.strip()` is never tested.
- **`describe_image()` error path untested**: When the API fails, the function returns an error message string -- this path is not tested.

---

## Missing Corner Cases

### `utils/images/normalize.py`
- Constant image (all same value) -- `v_high - v_low` approaches 0
- Single-pixel image
- Image with NaN or Inf values
- `p_low=0, p_high=100` (full range)
- `p_low=50, p_high=50` (same percentile)
- `clip=False` -- values outside [0,1] should be preserved

### `utils/configuration/app_configuration.py`
- Thread safety: concurrent access to the same `app_name`
- Configuration file with corrupt/invalid YAML
- Configuration file that exists but is empty (yaml.safe_load returns None)
- Keys with None values vs. missing keys in `get()` -- note that `get()` treats explicit `None` values the same as missing keys, which may be surprising
- The `__init__` re-runs `load_configurations()` every time even for a singleton, potentially losing in-memory state

### `utils/network/port_available.py`
- `find_first_port_available()` with `start == end` (empty range)
- `find_first_port_available()` with all ports occupied (should return None)
- Privilege-restricted ports (e.g., port 80)
- Non-integer or negative port numbers

### `utils/notebook/jupyter_notebook.py`
- `restart()` with `write_before_restart=True` when `file_path` is None (writes to default path)
- `restart()` when `_modified` is False and `force_restart` is False (should be a no-op)
- `add_code_cell()` with `remove_quotes=True` on code with no surrounding quotes
- `add_image_cell()` with non-existent image path
- `take_snapshot()` when no snapshot function is registered (AttributeError)
- `delete_notebook_file()` when file has never been written

### `utils/system/information.py`
- `system_info(add_python_info=True)` -- the True branch is never tested

### `utils/system/folders.py`
- `get_or_create_folder_in_home()` when folder already exists vs. when it needs creation
- Nested folder names (e.g., `"a/b/c"`) -- `os.mkdir()` would fail, but `os.makedirs()` would succeed

### `utils/async_utils/run_async.py`
- Calling `run_async()` from within an already-running event loop
- Calling `run_async()` with a synchronous function (error path)
- Exception propagation from the async function

### `utils/segmentation/labels_3d_merging.py`
- `make_slice_labels_different()` with a single-slice stack
- `merge_2d_segments()` with no overlapping segments
- `merge_2d_segments()` with `overlap_threshold=0` (everything merges)
- `remove_small_segments()` with `min_segment_size=0` (no-op path)
- Empty label arrays (all zeros)

---

## Redundant Tests

### `utils/openai/test/check_api_key_test.py`
- **`test_check_api_key_function_exists`**: Redundant -- if the import fails, every other test in the file will also fail. This test adds no value.
- **`test_check_api_key_returns_bool`** and **`test_check_api_key_with_invalid_key_returns_false`** overlap significantly: both call the function with an invalid key and check the return. The first checks `isinstance(result, bool)`, the second checks `result is False`. These could be a single test.
- **The three `inspect.getsource()` tests** (`test_check_api_key_uses_modern_openai_api`, `test_check_api_key_uses_openai_client`, `test_check_api_key_does_not_use_chatcompletion`) are all style-enforcement rather than behavioral tests and could be consolidated into a single test or replaced by a linter rule.

### `utils/notebook/test/jupyter_notebook_test.py`
- **`test_notebook_creation`**: The `delete_notebook_file()` call at the end does nothing (the notebook was never written to disk, so `file_path` is None).
- **`test_add_image_cell`**: Writes `test_notebook.ipynb` to the current working directory but then calls `notebook.delete_notebook_file()` which deletes based on the internal `file_path` attribute (set by `write()`), so this does clean up correctly. However, the test has no assertion about the image cell content -- it only prints a message asking for manual verification.

---

## Positive Findings

1. **`utils/openai/test/check_api_key_test.py`** provides good backward-compatibility checks by verifying the code does not use deprecated OpenAI v0.x patterns. While the approach (source inspection) is unusual, the intent is sound and caught a real migration issue.

2. **`utils/notebook/test/add_and_split_markdown_test.py`** is a well-constructed test that verifies a non-trivial code-block detection feature with a realistic, complex markdown input. It tests both the `detect_code_blocks=False` and `detect_code_blocks=True` paths and validates cell types and content.

3. **`utils/network/test/port_available_test.py`** actually starts a server and verifies the port is then detected as occupied. This is a proper integration test that validates real-world behavior rather than mocking everything.

4. **`utils/llm/test/vision_test.py`** and **`utils/llm/test/summarizer_test.py`** use appropriate `pytest.mark.skipif` decorators to conditionally skip when LLM services are not available, preventing CI failures.

5. **`utils/napari/test/napari_viewer_info_test.py`** is thorough in setting up the test fixture -- it creates one of every common layer type (Image, Labels, Points, Shapes, Surface, Tracks, Vectors), ensuring the info function exercises all its type-specific branches even though the assertions on the output are weak.

6. **`utils/configuration/test/app_configuration_test.py`** correctly tests the persistence roundtrip by creating a second instance and verifying it can read the first instance's saved values.

---

## Detailed Analysis per Package

### 1. `utils/configuration/`

**Source**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/configuration/app_configuration.py`
**Test**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/configuration/test/app_configuration_test.py`

`AppConfiguration` is a singleton-per-app-name configuration manager using YAML files stored in `~/.{app_name}/`. It merges default config with user config.

**Public API**:
| Method | Tested? |
|--------|---------|
| `__new__` (singleton) | Partially (second instance created but `__init__` re-runs) |
| `__init__` | Implicitly |
| `load_default_config()` | Only dict path; file path untested |
| `load_configurations()` | Implicitly |
| `save_configurations()` | Implicitly via `__setitem__` |
| `get(key, default)` | **Not tested** |
| `__getitem__` | Yes |
| `__setitem__` | Yes |

**Key issue**: The singleton pattern in `__new__` caches instances, but `__init__` always re-runs (resetting `config_data` by calling `load_configurations()`). This means in-memory changes that have not been saved to disk would be lost when constructing a second reference. The test does not surface this because `__setitem__` persists to disk immediately. However, the `get()` method's auto-persistence side effect (writing defaults back to disk) is completely untested and could mask bugs.

**Missing tests**:
- `get()` with and without default values
- YAML file as `default_config` argument
- Cleanup of test artifacts in `~/.test_app_configuration/`
- Concurrent access (thread safety claimed via Lock in `__new__`)

---

### 2. `utils/images/`

**Source**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/images/normalize.py`
**Test**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/images/test/normalize_test.py`

Single function `normalize_img()`. The test is a basic smoke test with one input.

**Missing tests**:
- `clip=False`
- Constant-value image
- Float input image
- Multi-dimensional images (3D, 4D)
- Extreme percentiles (0/100)

---

### 3. `utils/napari/`

**Sources**:
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/napari/layer_snapshot.py` -- **No tests**
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/napari/napari_viewer_info.py` -- 1 test file
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/napari/open_in_napari.py` -- **No tests**

**Test**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/napari/test/napari_viewer_info_test.py`

The test for `napari_viewer_info.py` creates a headless napari viewer with all layer types and calls `get_viewer_info()`, but only asserts the output is non-empty. Specific layer information (names, types, shapes, label counts) should be validated in the returned string.

`layer_snapshot.py` contains `capture_canvas_snapshot()` which manipulates viewer visibility and camera state -- this is tricky to test headlessly but could at minimum verify that visibility is properly restored after the snapshot.

`open_in_napari.py` has 5 public functions with a cascade of fallback strategies. None are tested. At minimum, the happy path of `open_in_napari()` with a simple image could be tested.

---

### 4. `utils/network/`

**Source**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/network/port_available.py`
**Test**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/network/test/port_available_test.py`

| Function | Tested? |
|----------|---------|
| `is_port_available()` | Yes (both available and occupied) |
| `find_first_port_available()` | **Not tested** |

The test is decent for `is_port_available()` -- it verifies both the available and occupied states. However, `find_first_port_available()` is a standalone function with its own logic (iteration + None return) and deserves its own test.

**Bug in test**: The error message says "No port available between 5000 and 6000" but the actual range is 9000-10000.

---

### 5. `utils/notebook/`

**Source**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/notebook/jupyter_notebook.py`
**Tests**:
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/notebook/test/jupyter_notebook_test.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/notebook/test/add_and_split_markdown_test.py`

| Method | Tested? |
|--------|---------|
| `__init__` | Yes (implicitly) |
| `restart()` | Not tested directly |
| `write()` | Yes (via `test_add_image_cell`) |
| `add_code_cell()` | Yes |
| `add_markdown_cell()` | Yes (both modes) |
| `_add_image()` | Implicitly |
| `add_image_cell()` | Yes (but no content assertion) |
| `add_image_cell_from_PIL_image()` | Not tested |
| `register_snapshot_function()` | Not tested |
| `take_snapshot()` | Not tested |
| `delete_notebook_file()` | Called but behavior not asserted |

**Issues**:
- `test_add_image_cell` downloads an image from Wikipedia during test execution, making it flaky on CI without network access.
- `test_add_image_cell` has no assertions on the notebook cell content.
- `add_code_cell()` with `remove_quotes=True` is not tested.
- `restart()` logic (modified flag, write-before-restart) is not tested.

---

### 6. `utils/openai/`

**Sources**:
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/openai/check_api_key.py` -- Tested
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/openai/default_model.py` -- Tested (integration)
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/openai/max_token_limit.py` -- **No tests**
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/openai/model_list.py` -- Tested (integration)

**`max_token_limit.py` is completely untested.** This is a simple deterministic function with 6 branches that maps model names to token limits. It is trivially testable without any API access:

```python
# max_token_limit.py branches:
# "gpt-4-1106-preview" -> 128000
# "32k" -> 32000
# "16k" -> 16385
# "gpt-4" -> 8192
# "gpt-3.5-turbo-1106" -> 16385
# "gpt-3.5" -> 4096
# default -> 4096
```

**`postprocess_openai_model_list()` in `model_list.py` is untested.** This is a pure function that sorts and filters a list of model names. It could be tested entirely offline.

---

### 7. `utils/llm/`

**Sources**:
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/llm/summarizer.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/llm/vision.py`

**Tests**:
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/llm/test/summarizer_test.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/llm/test/vision_test.py`

Both test files are integration tests that require live LLM access. They are properly gated with `skipif` decorators.

**Missing**:
- Unit tests with mocked LLMs for deterministic testing
- `summarize("")` (empty string input, should return empty string)
- `describe_image()` with non-existent file path (error path)
- `is_vision_available()` when no API is configured (the `except` branch)

---

### 8. `utils/system/`

**Sources**:
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/system/folders.py` -- **No tests**
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/system/information.py` -- Tested
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/system/is_apple_silicon.py` -- **No tests**

**Test**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/system/test/system_information_test.py`

The test for `system_info()` only checks that certain keys appear in the output string, and only tests `add_python_info=False`. When `add_python_info=True`, the output should also contain "Python Version", "Python Compiler", etc. -- this is untested.

`folders.py` has two simple but important functions. `get_or_create_folder_in_home()` uses `os.mkdir()` which cannot create nested directories -- this is a latent bug that tests would have surfaced.

`is_apple_silicon()` is platform-dependent and could be tested with `unittest.mock.patch` on `platform.system()` and `os.uname()`.

---

### 9. `utils/segmentation/`

**Sources**:
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/segmentation/labels_3d_merging.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/segmentation/remove_small_segments.py`

**Tests**: None (no test directory at all).

This is the most concerning gap. The 3D label merging code is algorithmically complex, involving:
- Multi-axis 2D segmentation with transposition
- Binary mask intersection
- Morphological operations
- Label renumbering across slices
- Overlap-based merging with threshold

All of these are prime candidates for subtle bugs. The `merge_2d_segments()` function also contains a debugging `napari.run()` call gated by `debug_view`, which would hang tests if accidentally enabled.

`remove_small_segments.py` is a thin wrapper around `skimage.morphology.remove_small_objects` with a `min_segment_size > 0` guard. Even this should have a basic test.

---

### 10. `utils/download/`

**Source**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/download/download_files.py`
**Tests**: Empty test directory (only `__init__.py`).

Two public functions:
1. `download_files(urls, path)` -- basic `urllib.request.urlretrieve` wrapper
2. `download_file_stealth(url, file_path)` -- uses `requests` with browser-like headers

Neither is tested. `download_file_stealth` has a potential resource leak: when `file_path` is provided, the file is opened with `open()` (line 56) but if an exception occurs during `response.iter_content()`, the `with` block handles cleanup. However, the function returns `None` on HTTP errors without raising, which could silently fail.

---

### 11. `utils/async_utils/`

**Source**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/async_utils/run_async.py`
**Tests**: No test directory or file.

`run_async()` has two execution paths:
1. When a running event loop exists: spawns a `_RunThread` which calls `asyncio.run()` in a new thread
2. When no running loop: calls `asyncio.run()` directly

Both paths are untested. The thread-based path is particularly important to test as it is the mechanism used for safe async execution from within napari's Qt event loop.

---

### 12. `utils/anthropic/`

**Source**: `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/utils/anthropic/model_list.py`
**Tests**: No test directory or file.

The function returns a hardcoded list of model names. While trivial, a test verifying the list is non-empty and that all entries match expected naming conventions (e.g., start with `"claude-"`) would catch copy-paste errors when the list is updated.
