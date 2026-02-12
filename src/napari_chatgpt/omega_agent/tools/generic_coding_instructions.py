"""Generic code-generation instructions shared across all napari tools.

The ``omega_generic_codegen_instructions`` template is formatted at
runtime with the current Python version and list of installed packages,
then prepended to each tool's specific instructions before being sent
to the sub-LLM for code generation.
"""

omega_generic_codegen_instructions = """
**Coding Strategy:**
1. Plan your approach step by step before coding.
2. Write a single, complete, and functional block of Python code.

**Python Code Guidelines:**
- Ensure the code is self-contained, with no missing parts, data, or calculations.
- Use only functions from the standard Python {python_version} library and the installed packages listed here: "{packages}". Only use parameters you are certain exist in the relevant package version.
- Output the code as a single contiguous Python code block (```python ...code... ```).
- Keep lines concise. Break long lines and align named parameters for readability.
- When needed, import `ArrayLike` from `numpy.typing`.
- Match the dtype and format expected by each library (e.g., uint8 BGR for OpenCV, supported PyTorch dtypes, low-level operations for Numba).

**Napari Viewer Rules:**
- A napari viewer instance is available as `viewer`. Never create a new `napari.Viewer()`.
- Do not call `gui_qt()`.
- To get the selected layer: `viewer.layers.selection.active`.
- To access a layer by name: `viewer.layers["layer_name"]` (raises `KeyError` if not found). Do NOT use `viewer.layers.get(...)` — `LayerList` has no `.get()` method.
- Napari layers do not have a 'type' field. To check a layer's type, use: `isinstance(layer, napari.layers.Shapes)`.
- To rotate the camera: `viewer.camera.angles = (angle_z, angle_y, angle_x)`.
- **IMPORTANT napari 0.5+ API change for Points layers:** `viewer.add_points()` uses `border_color` and `border_width` (NOT `edge_color`/`edge_width`). Shapes and Vectors layers still use `edge_color`/`edge_width`.
- Write only safe code that does not delete files or perform destructive actions.
- Always end code with a `print()` statement summarizing what was accomplished.

**Image Array Conventions:**
- Convert image arrays to `float32` before processing when appropriate.
- Use float values for constants (e.g., `1.0` not `1` in `np.full()`, `np.ones()`, `np.zeros()`).
- RGB/RGBA images must be `uint8` in [0, 255] to display correctly in napari.
- Labels arrays must remain integer type (e.g., `uint32`).

**Layer Reference Conventions:**
- "this/that/the image/layer" refers to the last added layer.
- If unsure which layer is referenced, use the last layer of the most relevant type.
- "selected image" means `viewer.layers.selection.active`.

"""
