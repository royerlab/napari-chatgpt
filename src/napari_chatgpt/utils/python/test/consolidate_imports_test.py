from napari_chatgpt.utils.python.consolidate_imports import consolidate_imports

code_to_consolidate_imports = """
    import napari
    import numpy as np
    from scipy.ndimage import gaussian_filter
    
    
    
    
    import napari
    import numpy as np
    from scipy.ndimage import gaussian_filter
    
    # Step 1: Retrieve the selected image layer from the viewer.
    selected_image_layer = viewer.layers.selection.active
    
    # Step 2: Convert the image data to float type if it's not already.
    image_data = np.asarray(selected_image_layer.data, dtype=float)
    
    # Step 3: Apply a Gaussian filter with sigma=2 to the image data.
    filtered_image_data = gaussian_filter(image_data, sigma=2)
    
    # Step 4: Add the filtered image as a new layer to the viewer.
    viewer.add_image(filtered_image_data, name=f"{selected_image_layer.name}_gaussian_filtered")
    
    # Step 5: Print the result of the operation.
    print("Applied a Gaussian filter with sigma=2 to the selected image.")
    """


def test_consolidate_imports():
    result = consolidate_imports(code_to_consolidate_imports)

    print("")
    print(result)

    # Check that duplicate imports were removed
    assert result.count("import napari") == 1
    assert result.count("import numpy as np") == 1
    assert result.count("from scipy.ndimage import gaussian_filter") == 1

    # Check that code content is preserved
    assert "selected_image_layer = viewer.layers.selection.active" in result
    assert "gaussian_filter(image_data, sigma=2)" in result
    assert "viewer.add_image" in result

    # Check that the result is shorter than the original (duplicates removed)
    assert len(result.split("\n")) < len(code_to_consolidate_imports.split("\n"))


def test_consolidate_imports_empty_string():
    result = consolidate_imports("")
    assert result == ""


def test_consolidate_imports_no_imports():
    code = "x = 1\ny = 2\n"
    result = consolidate_imports(code)
    assert "x = 1" in result
    assert "y = 2" in result


def test_consolidate_imports_only_imports():
    code = "import os\nimport sys\nimport os\n"
    result = consolidate_imports(code)
    assert result.count("import os") == 1
    assert result.count("import sys") == 1


def test_consolidate_imports_deduplicates():
    code = "import numpy\nimport numpy\nimport pandas\n\nx = 1\n"
    result = consolidate_imports(code)
    assert result.count("import numpy") == 1
    assert result.count("import pandas") == 1
    assert "x = 1" in result


def test_consolidate_imports_blank_lines_between():
    code = "import os\n\n\n\nimport sys\n\n\nx = 1\n"
    result = consolidate_imports(code)
    assert result.count("import os") == 1
    assert result.count("import sys") == 1
    assert "x = 1" in result
