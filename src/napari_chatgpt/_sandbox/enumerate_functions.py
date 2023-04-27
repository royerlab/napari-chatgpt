import skimage

skimage_path = skimage.__file__
print(skimage_path)

import os
import glob

package_path = os.path.dirname(
    skimage_path)  # Replace with the actual package path

# Use os.path.join to construct the path to the package directory
package_dir = os.path.join(package_path, '*')

# Use glob to get a list of all the .py files in the package directory
module_files = glob.glob(os.path.join(package_dir, '*.py'), recursive=True)

# # Iterate over the module files and print the module names
# for module_file in module_files:
#     module_name: str = os.path.splitext(os.path.basename(module_file))[0]
#     if not module_name.startswith('_'):
#         print(module_name)

# Use os.walk to iterate over all files in the package directory and its subdirectories
for root, dirs, files in os.walk(package_path):
    # Iterate over all the files in the current directory
    for filename in files:
        # Check if the file is a Python file
        if filename.endswith('.py'):
            # Construct the module name from the file path
            module_name = os.path.splitext(
                os.path.relpath(os.path.join(root, filename), package_path))[
                0].replace('/', '.')
            print(module_name)
