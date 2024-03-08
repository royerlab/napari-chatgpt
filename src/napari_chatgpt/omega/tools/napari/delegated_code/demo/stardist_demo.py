from napari_chatgpt.omega.tools.napari.delegated_code.test.stardist_test import \
    test_stardist_2d, test_stardist_3d

if __name__ == '__main__':
    test_stardist_2d(show_viewer=True)
    test_stardist_3d(show_viewer=True)