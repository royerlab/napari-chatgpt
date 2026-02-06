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
