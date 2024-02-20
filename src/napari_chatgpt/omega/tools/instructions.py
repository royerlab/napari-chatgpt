
omega_generic_codegen_instructions = """

**Coding Strategy:**
- First, think step-by-step about how to implement the request.
- Second, describe these steps.
- Third, write the corresponding code.

**Generic Python Code Instructions:**
- Ensure that the code is complete and functional without any missing code, data, or calculations.
- Utilize functions exclusively from the standard Python {python_version} library.
- Utilize functions exclusively from the installed libraries mentioned in this list: "{packages}". Write your code based on the installed version of these libraries.
- ONLY USE parameters or arguments of functions that you are certain exist in the corresponding package or library version!
- Import all necessary libraries. For example, if you use the function scipy.signal.convolve2d(), include the statement: import scipy
- The code generated should a single contiguous block of Python code (```python <...code...> ```).
- When creating a copy of an array, avoid using this format: array_like.copy(). Instead, use np.copy(array_like).
- NEVER utilize the input() function to request additional information from me!
- Avoid long lines of code. If a line of code is too long, break it up into multiple lines, and align items such as named parameters.
- Remember that OpenCV requires uint8 BGR color channels, do not convert images to float before passing to OpenCV.
- When and if you use PyTorch functions make sure to pass tensors with the right dtype and number of dimensions in order to match PyTorch's functions parameter requirements. For instance, add and remove batch dimensions and convert to a compatible dtype before and after a series of calls to PyTorch functions.
- The only data types supported by PyTorch are: float32, float64, float16, bfloat16, uint8, int8, int16, int32, int64, and bool. Make sure to convert the input to one of these types before passing it to a PyTorch function.
- When using Numba to write image processing code make sure to avoid high-level numpy functions and instead implement the algorithms with loops and low-level numpy functions. Also, make sure to use the right data types for the input and output arrays.
- If you need to get the selected layer in the napari viewer, use the following code: `viewer.layers.selection.active` .
- If you need to rotate the viewer camera to a specific set of angles, use the following code: `viewer.camera.angles = (angle_z, angle_y, angle_x)`  .
"""

