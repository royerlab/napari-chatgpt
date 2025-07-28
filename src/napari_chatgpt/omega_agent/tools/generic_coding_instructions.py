omega_generic_codegen_instructions = \
"""
**Coding Strategy:**
1. Carefully plan your approach step by step before coding.
2. Clearly describe each step of your implementation.
3. Write a single, complete, and functional block of Python code.

**Python Code Guidelines:**
- Ensure the code is self-contained, with no missing parts, data, or calculations.
- Use only functions from the standard Python {python_version} library and the installed packages listed here: "{packages}". Always check the installed version for compatibility.
- Only use parameters or arguments you are certain exist in the relevant package or library version.
- Import all required libraries explicitly. For example, if using `scipy.signal.convolve2d()`, include `import scipy`.
- Output the code as a single contiguous Python code block (```python ...code... ```).
- When copying arrays, use `np.copy(array_like)` instead of `array_like.copy()`.
- Do not use the `input()` function to request information.
- Keep lines concise. Break long lines and align named parameters for readability.
- To get the selected layer in a napari viewer, use: `viewer.layers.selection.active`.
- Napari layers do not have a 'type' field. To check a layer's type, use: `isinstance(layer, napari.layers.Shapes)`, for example.
- To rotate the napari viewer camera to specific angles, use: `viewer.camera.angles = (angle_z, angle_y, angle_x)`.
- When needed, import `ArrayLike` from `numpy.typing`.

**Library and Package Specific Instructions:**
- For OpenCV, ensure images are in uint8 BGR format; do not convert to float before passing to OpenCV functions.
- When using PyTorch, ensure tensors have the correct dtype and dimensions. Add or remove batch dimensions and convert dtypes as needed to match function requirements.
- PyTorch supports only these data types: float32, float64, float16, bfloat16, uint8, int8, int16, int32, int64, and bool. Convert inputs to one of these types before using PyTorch functions.
- When using Numba for image processing, avoid high-level NumPy functions. Use loops and low-level NumPy operations, and ensure correct data types for input and output arrays.


"""
