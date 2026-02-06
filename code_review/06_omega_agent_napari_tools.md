# Code Review: Omega Agent Napari Tools

**Review Date:** 2026-02-05
**Reviewer:** Claude Opus 4.5
**Scope:** `src/napari_chatgpt/omega_agent/tools/napari/` and `delegated_code/` subdirectory

---

## Executive Summary

The omega_agent napari tools provide a sophisticated framework for LLM-driven code generation and execution within napari. The architecture is well-designed with clear separation between tool classes, delegated segmentation/denoising code, and utility functions. However, there are several areas requiring attention, particularly around security (arbitrary code execution), type annotations, error handling edge cases, and test coverage gaps.

**Overall Assessment:** The codebase is functional and well-organized but has notable security considerations inherent to its design (executing LLM-generated code) and several medium-priority improvements that would enhance robustness.

---

## Table of Contents

1. [Code Quality](#1-code-quality)
2. [Logic and Correctness](#2-logic-and-correctness)
3. [Type Annotations](#3-type-annotations)
4. [Documentation](#4-documentation)
5. [Architecture](#5-architecture)
6. [Security](#6-security)
7. [Test Coverage](#7-test-coverage)
8. [Summary of Findings](#8-summary-of-findings)

---

## 1. Code Quality

### 1.1 Style Consistency

**Severity: Low**

The codebase generally follows Python conventions and PEP 8 guidelines. Pre-commit hooks enforce black formatting and isort import ordering.

#### Issues Found:

**Issue 1.1.1: Inconsistent string quote usage in prompts**
- **File:** Multiple tool files
- **Observation:** Long prompts use triple double-quotes consistently, but inline strings mix single and double quotes arbitrarily.
- **Recommendation:** Consider using f-strings with consistent quote style throughout.

**Issue 1.1.2: Typo in test function name**
- **File:** `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/delegated_code/test/classic_test.py`
- **Lines:** 10, 47
- **Code:**
  ```python
  def test_classsic_2d(show_viewer: bool = False):
  def test_classsic_3d(show_viewer: bool = False):
  ```
- **Issue:** Function names have typo "classsic" instead of "classic"
- **Recommendation:** Rename to `test_classic_2d` and `test_classic_3d`

**Issue 1.1.3: Redundant f-string without placeholders**
- **File:** `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/cell_nuclei_segmentation_tool.py`
- **Lines:** 220, 221, 250, 260
- **Code:**
  ```python
  with asection(f"CellNucleiSegmentationTool:"):
      with asection(f"Request:"):
  ```
- **Issue:** f-strings with no placeholders waste resources
- **Recommendation:** Remove f-prefix: `with asection("CellNucleiSegmentationTool:"):`

### 1.2 Naming Conventions

**Severity: Low**

**Issue 1.2.1: Underscore-prefixed module-level functions inconsistently used**
- **File:** `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/viewer_vision_tool.py`
- **Lines:** 143, 207, 221
- **Observation:** Helper functions `_get_description_for_selected_layer`, `_get_description_for_whole_canvas`, and `_get_layer_image_description` are module-level but could be class methods.
- **Recommendation:** Consider moving these to class methods or a dedicated utility module for better organization.

### 1.3 Code Organization

**Severity: Low**

**Issue 1.3.1: Unused imports in cell_nuclei_segmentation_tool.py**
- **File:** `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/cell_nuclei_segmentation_tool.py`
- **Line:** 3
- **Code:**
  ```python
  import sys
  ```
- **Issue:** `sys` is imported but only used in `stardist_package_massaging()` which appears to be incomplete/unused
- **Recommendation:** Remove unused imports or complete the implementation

**Issue 1.3.2: Dead code - stardist_package_massaging and purge_tensorflow**
- **File:** `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/cell_nuclei_segmentation_tool.py`
- **Lines:** 298-337
- **Observation:** These functions appear to be unused and incomplete (missing return statement in `stardist_package_massaging`, unreachable code after `return`)
- **Recommendation:** Either complete the implementation or remove dead code

---

## 2. Logic and Correctness

### 2.1 Bugs and Edge Cases

**Severity: High**

**Issue 2.1.1: Potential NoneType access in viewer_vision_tool.py**
- **File:** `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/viewer_vision_tool.py`
- **Lines:** 77-85
- **Code:**
  ```python
  if (
      match
      or "*selected*" in query
      or "*active*" in query
      or "*current*" in query
  ):
      # Extract the layer name from match:
      layer_name = match.group(1)  # match could be None here!
  ```
- **Issue:** If `match` is None but one of the `*selected*`, `*active*`, `*current*` conditions is True, `match.group(1)` will raise AttributeError.
- **Recommendation:** Restructure the conditional logic:
  ```python
  if "*selected*" in query or "*active*" in query or "*current*" in query:
      layer_name = "selected"  # or appropriate keyword
  elif match:
      layer_name = match.group(1)
  else:
      # handle no match case
  ```

**Issue 2.1.2: Missing return type conversion in cellpose.py for 2D case**
- **File:** `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/delegated_code/cellpose.py`
- **Lines:** 92-112
- **Code:**
  ```python
  if len(image.shape) == 2:
      labels = model.eval(...)[0]
  elif len(image.shape) == 3:
      labels = model.eval(...)[0]
  # Missing else clause for invalid dimensions
  # labels could be undefined if image.shape has unexpected length
  ```
- **Issue:** If `len(image.shape)` is not 2 or 3 (e.g., 1D array passed), `labels` will be undefined
- **Note:** There's a check at line 72-73 that catches >3D, but 1D arrays would slip through
- **Recommendation:** Add explicit else clause or modify the initial check:
  ```python
  if len(image.shape) < 2 or len(image.shape) > 3:
      raise ValueError("The input image must be 2D or 3D.")
  ```

**Severity: Medium**

**Issue 2.1.3: Incomplete sentence in prompt**
- **File:** `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/cell_nuclei_segmentation_tool.py`
- **Lines:** 128
- **Code:**
  ```python
  - If the request (below) asks for segmentation with a specific algorithm that is not available (above), then .
  ```
- **Issue:** Sentence is incomplete (ends with "then .")
- **Recommendation:** Complete the instruction, e.g., "then explain that the algorithm is not available and suggest alternatives."

**Issue 2.1.4: Case-sensitive function name matching**
- **File:** `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/cell_nuclei_segmentation_tool.py`
- **Lines:** 233-245
- **Code:**
  ```python
  code_lower = code.lower()
  if "cellpose_segmentation(" in code_lower:
      segmentation_code = _get_delegated_code("cellpose")
  ```
- **Issue:** While the check uses lowercase, the actual function names in delegated code are mixed case. If LLM generates `Cellpose_Segmentation(`, it would match the lowercase check but might cause issues during execution.
- **Recommendation:** The current approach is acceptable but document this behavior.

**Issue 2.1.5: Hardcoded expected label counts in tests**
- **File:** `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/delegated_code/test/cellpose_test.py`
- **Lines:** 34, 71
- **Code:**
  ```python
  assert nb_unique_labels == 24  # 2D test
  assert nb_unique_labels == 36  # 3D test
  ```
- **Issue:** These exact counts may vary with different cellpose versions, making tests brittle
- **Recommendation:** Use range assertions:
  ```python
  assert 20 <= nb_unique_labels <= 30  # Allow some variance
  ```

### 2.2 Error Handling

**Severity: Medium**

**Issue 2.2.1: Generic exception handling loses context**
- **File:** Multiple tool files (viewer_control_tool.py, viewer_execution_tool.py, etc.)
- **Pattern:**
  ```python
  except Exception as e:
      traceback.print_exc()
      return f"Error: {type(e).__name__} with message: '{str(e)}' occurred..."
  ```
- **Issue:** While the error is logged, the original traceback is only printed, not preserved in the return value. This makes debugging difficult for users.
- **Recommendation:** Consider including a truncated traceback in the return message or logging to a file.

**Issue 2.2.2: Silent failure in file_open_tool.py**
- **File:** `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/file_open_tool.py`
- **Lines:** 73-86
- **Code:**
  ```python
  try:
      success = open_in_napari(viewer, line, plugin=plugin)
      if success:
          opened_files.append(line)
      # What if success is False but no exception?
  except Exception as e:
      ...
  ```
- **Issue:** If `open_in_napari` returns False without raising an exception, the file is silently skipped without adding to errors list.
- **Recommendation:** Handle False return value:
  ```python
  if success:
      opened_files.append(line)
  else:
      encountered_errors.append(f"Failed to open '{line}' (no exception raised)")
  ```

---

## 3. Type Annotations

### 3.1 Completeness

**Severity: Medium**

**Issue 3.1.1: Missing return type annotations on tool methods**
- **Files:** All tool files
- **Pattern:**
  ```python
  def _run_code(self, request: str, code: str, viewer: Viewer) -> str:
  ```
- **Observation:** Return types are present on `_run_code` but missing on many helper functions.

**Issue 3.1.2: Inconsistent Optional typing style**
- **File:** `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/delegated_code/cellpose.py`
- **Lines:** 13-19
- **Code:**
  ```python
  normalize: bool | None = True,
  norm_range_low: float | None = 1.0,
  ```
- **File:** `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/delegated_code/signatures.py`
- **Code:**
  ```python
  normalize: Optional[bool] = True,
  norm_range_low: Optional[float] = 1.0,
  ```
- **Issue:** Mixing `X | None` (Python 3.10+) with `Optional[X]` syntax
- **Recommendation:** Standardize on `X | None` throughout since project requires Python 3.10+

**Issue 3.1.3: Missing type annotations in stardist.py helper functions**
- **File:** `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/delegated_code/stardist.py`
- **Lines:** 94, 107
- **Code:**
  ```python
  def stardist_2d(image, scale: float, model_type: str, model: Any | None = None):
  def stardist_3d(image, scale: float, model_type: str, min_segment_size: int):
  ```
- **Issue:** `image` parameter lacks type annotation, return types missing
- **Recommendation:**
  ```python
  def stardist_2d(image: ArrayLike, scale: float | None, model_type: str, model: Any | None = None) -> ndarray:
  def stardist_3d(image: ArrayLike, scale: float | None, model_type: str, min_segment_size: int) -> ndarray:
  ```

**Issue 3.1.4: Aydin delegated code lacks type annotations**
- **Files:** `aydin_classic.py`, `aydin_fgr.py`
- **Code:**
  ```python
  def aydin_classic_denoising(image, batch_axes=None, chan_axes=None, variant=None):
  ```
- **Issue:** No type hints at all
- **Recommendation:** Add complete type annotations:
  ```python
  def aydin_classic_denoising(
      image: np.ndarray,
      batch_axes: tuple[int, ...] | None = None,
      chan_axes: tuple[int, ...] | None = None,
      variant: str | None = None
  ) -> np.ndarray:
  ```

---

## 4. Documentation

### 4.1 Docstrings

**Severity: Low**

**Issue 4.1.1: Missing docstrings on helper functions**
- **File:** `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/delegated_code/utils.py`
- **Lines:** 5-22
- **Code:**
  ```python
  def check_stardist_installed() -> bool:
      try:
          import stardist  # noqa: F401
          return True
      except ImportError:
          return False
  ```
- **Issue:** Function lacks docstring explaining its purpose
- **Recommendation:** Add docstrings:
  ```python
  def check_stardist_installed() -> bool:
      """Check if the stardist package is available for import.

      Returns
      -------
      bool
          True if stardist can be imported, False otherwise.
      """
  ```

**Issue 4.1.2: Inconsistent docstring format**
- **Observation:** Some files use NumPy docstring style, others use Google style or none at all.
- **Recommendation:** Standardize on NumPy style (already used in most tool classes).

### 4.2 Comments Quality

**Severity: Low**

**Issue 4.2.1: Outdated/misleading comments**
- **File:** `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/delegated_code/signatures.py`
- **Lines:** 1-2
- **Code:**
  ```python
  # Cellpose is better for segmenting non-convex cells... only work in 2D
  ```
- **Issue:** Comment says "only work in 2D" but the implementation handles 3D images via slice-by-slice processing
- **Recommendation:** Update comment to reflect actual capability.

---

## 5. Architecture

### 5.1 Tool Design

**Severity: Low**

**Positive Observations:**
- Clean inheritance hierarchy: `BaseOmegaTool` -> `BaseNapariTool` -> Specific tools
- Queue-based communication pattern is well-implemented for thread safety
- Delegated code pattern allows clean separation of algorithm implementations

**Issue 5.1.1: Code duplication across similar tools**
- **Files:** `viewer_control_tool.py`, `viewer_execution_tool.py`
- **Observation:** These two tools have nearly identical `_run_code` implementations (lines 91-122 in both files)
- **Recommendation:** Extract common logic to base class or mixin.

**Issue 5.1.2: Tight coupling with MicroPluginMainWindow**
- **Pattern in multiple files:**
  ```python
  from napari_chatgpt.microplugin.microplugin_window import MicroPluginMainWindow
  MicroPluginMainWindow.add_snippet(filename=filename, code=code)
  ```
- **Issue:** Import inside method creates hidden dependency, makes testing difficult
- **Recommendation:** Inject snippet handler as dependency or use event-based decoupling.

### 5.2 napari Integration Patterns

**Severity: Low**

**Positive Observations:**
- Proper use of napari layer types and viewer API
- Vision tool correctly handles layer selection edge cases
- File open tool properly handles plugin specification

**Issue 5.2.1: Private API usage**
- **File:** `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/viewer_vision_tool.py`
- **Line:** 184
- **Code:**
  ```python
  current_layer = selected_layers._current
  ```
- **Issue:** Using private `_current` attribute which may change in future napari versions
- **Recommendation:** Use public API if available, or document the version dependency.

---

## 6. Security

### 6.1 Code Execution Safety

**Severity: Critical**

**Issue 6.1.1: Arbitrary code execution from LLM output**
- **Files:** All tool files using `dynamic_import` and `execute_as_module`
- **Pattern:**
  ```python
  loaded_module = dynamic_import(code)
  function = getattr(loaded_module, function_name)
  result = function(viewer)
  ```
- **Issue:** LLM-generated code is executed with full privileges. Despite prompt instructions, a malicious or confused LLM could generate dangerous code.
- **Current Mitigations:**
  - Prompt instructions request safe code
  - `check_code_safety.py` utility exists but is not consistently used
  - Some line filtering in `_prepare_code()`
- **Recommendations:**
  1. **Always** run `check_code_safety()` before execution
  2. Consider sandboxing options (restricted builtins, resource limits)
  3. Implement user confirmation for safety ratings below threshold
  4. Add AST-based static analysis for dangerous patterns:
     ```python
     DANGEROUS_PATTERNS = [
         'os.system', 'subprocess', 'eval', 'exec',
         '__import__', 'open(..., "w")', 'shutil.rmtree'
     ]
     ```

**Issue 6.1.2: Incomplete filtering of dangerous code patterns**
- **File:** `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/base_napari_tool.py`
- **Lines:** 249-258
- **Code:**
  ```python
  code = filter_lines(
      code,
      [
          "napari.Viewer(",
          "= Viewer(",
          "gui_qt(",
          "viewer.window.add_dock_widget(",
      ],
  )
  ```
- **Issue:** This filters napari-related issues but not security threats
- **Recommendation:** Expand filtering to include dangerous system operations.

### 6.2 Input Validation

**Severity: High**

**Issue 6.2.1: No validation of file paths in file_open_tool.py**
- **File:** `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/file_open_tool.py`
- **Lines:** 56-77
- **Code:**
  ```python
  for line in lines:
      line = line.strip()
      # ... no path validation ...
      success = open_in_napari(viewer, line, plugin=plugin)
  ```
- **Issue:** File paths are passed directly without validation. Could potentially be exploited for path traversal.
- **Recommendation:** Validate paths:
  ```python
  import os
  resolved_path = os.path.realpath(line)
  # Check if path is within allowed directories
  # Reject paths with suspicious patterns like '..' repeated
  ```

**Issue 6.2.2: Plugin name not validated**
- **File:** `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/file_open_tool.py`
- **Lines:** 67-70
- **Code:**
  ```python
  if "[" in line and "]" in line:
      plugin = line[line.index("[") + 1 : line.index("]")].strip()
  ```
- **Issue:** Plugin name extracted without validation against known plugins
- **Recommendation:** Validate against napari's plugin registry.

### 6.3 Package Installation

**Severity: High**

**Issue 6.3.1: Automatic pip install without user consent**
- **File:** `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/base_napari_tool.py`
- **Lines:** 262-267
- **Code:**
  ```python
  if self.install_missing_packages and do_install_missing_packages:
      packages = required_packages(code, llm=self.llm)
      pip_install(packages)
  ```
- **Issue:** Packages are installed automatically based on LLM analysis of generated code. This could install malicious packages.
- **Recommendation:**
  1. Add user confirmation dialog before installation
  2. Maintain allowlist of trusted packages
  3. Log all installation attempts

---

## 7. Test Coverage

### 7.1 Coverage Analysis

**Severity: Medium**

**Files with Tests:**
- `delegated_code/test/cellpose_test.py` - Tests 2D and 3D segmentation
- `delegated_code/test/stardist_test.py` - Tests 2D and 3D segmentation
- `delegated_code/test/classic_test.py` - Tests 2D and 3D segmentation
- `delegated_code/test/utils_test.py` - Tests utility functions
- `delegated_code/test/stardist_imports_test.py` - Tests import functionality
- `test/image_denoising_tool_test.py` - Tests fix verification
- `test/file_open_tool_test.py` - Tests fix verification

**Files Missing Tests:**
- `viewer_control_tool.py` - No tests
- `viewer_execution_tool.py` - No tests
- `viewer_query_tool.py` - No tests
- `viewer_vision_tool.py` - No tests
- `widget_maker_tool.py` - No tests
- `cell_nuclei_segmentation_tool.py` - No dedicated tests (only delegated code tested)

### 7.2 Test Quality Issues

**Issue 7.2.1: Tests rely on exact numeric assertions**
- **Files:** All `*_test.py` files
- **Pattern:**
  ```python
  assert nb_unique_labels == 24
  ```
- **Issue:** Exact counts can vary with library versions, random seeds
- **Recommendation:** Use range-based or relative assertions.

**Issue 7.2.2: No error case testing**
- **Observation:** Tests only cover happy paths
- **Missing Tests:**
  - Invalid image dimensions
  - Empty images
  - Invalid model types
  - Network failures (for tools that download)
- **Recommendation:** Add parametrized tests for error cases:
  ```python
  @pytest.mark.parametrize("shape", [(10,), (10, 10, 10, 10)])
  def test_cellpose_invalid_dimensions(shape):
      with pytest.raises(ValueError):
          cellpose_segmentation(np.zeros(shape))
  ```

**Issue 7.2.3: No integration tests for tool classes**
- **Observation:** Tool classes are not tested end-to-end
- **Recommendation:** Add integration tests that mock the LLM and verify tool behavior with napari fixtures.

**Issue 7.2.4: Demo files duplicate test logic**
- **Files:** `demo/cellpose_demo.py`, `demo/stardist_demo.py`, `demo/classic_demo.py`
- **Observation:** These simply import and run test functions
- **Recommendation:** Either remove redundancy or add unique demo functionality.

---

## 8. Summary of Findings

### By Severity

| Severity | Count | Categories |
|----------|-------|------------|
| Critical | 1 | Security (arbitrary code execution) |
| High | 4 | Security (input validation, auto pip install), Logic bugs |
| Medium | 7 | Type annotations, Error handling, Test coverage |
| Low | 10 | Code quality, Documentation, Architecture |

### Priority Recommendations

1. **Immediate (Critical/High):**
   - Implement mandatory code safety checks before execution
   - Add user confirmation for package installation
   - Validate file paths and plugin names
   - Fix NoneType access bug in viewer_vision_tool.py

2. **Short-term (Medium):**
   - Standardize type annotations across all files
   - Improve error handling with better context preservation
   - Add tests for tool classes and error cases
   - Fix the incomplete prompt sentence

3. **Long-term (Low):**
   - Refactor common tool logic to reduce duplication
   - Update documentation and docstrings
   - Remove dead code (stardist_package_massaging, purge_tensorflow)
   - Fix typos in test function names

### Positive Aspects

1. **Clean Architecture:** The tool hierarchy and delegation pattern is well-designed
2. **Good napari Integration:** Proper use of viewer API and layer types
3. **Thread Safety:** Queue-based communication handles Qt thread requirements correctly
4. **Comprehensive Prompts:** LLM prompts are detailed and well-structured
5. **Recent Bug Fixes:** Evidence of recent fixes (stardist imports, platform detection)

---

## Appendix: Files Reviewed

### Main Tool Files
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/__init__.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/cell_nuclei_segmentation_tool.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/file_open_tool.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/image_denoising_tool.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/viewer_control_tool.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/viewer_execution_tool.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/viewer_query_tool.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/viewer_vision_tool.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/widget_maker_tool.py`

### Delegated Code Files
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/delegated_code/cellpose.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/delegated_code/stardist.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/delegated_code/classic.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/delegated_code/aydin_classic.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/delegated_code/aydin_fgr.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/delegated_code/signatures.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/delegated_code/utils.py`

### Test Files
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/delegated_code/test/cellpose_test.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/delegated_code/test/stardist_test.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/delegated_code/test/classic_test.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/delegated_code/test/utils_test.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/delegated_code/test/stardist_imports_test.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/test/image_denoising_tool_test.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/napari/test/file_open_tool_test.py`

### Base Classes
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/base_napari_tool.py`
- `/home/royer/workspace/python/napari-chatgpt/src/napari_chatgpt/omega_agent/tools/base_omega_tool.py`
