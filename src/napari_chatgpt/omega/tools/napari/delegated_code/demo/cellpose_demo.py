from napari_chatgpt.omega.tools.napari.delegated_code.test.cellpose_test import \
    test_cellpose_2d, test_cellpose_3d

if __name__ == '__main__':
    test_cellpose_2d(show_viewer=True)
    test_cellpose_3d(show_viewer=True)