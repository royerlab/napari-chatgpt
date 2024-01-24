
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
"""

