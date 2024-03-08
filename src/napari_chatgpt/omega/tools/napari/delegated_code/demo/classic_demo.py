from napari_chatgpt.omega.tools.napari.delegated_code.test.classic_test import \
    test_classsic_2d, test_classsic_3d

if __name__ == '__main__':
    test_classsic_2d(show_viewer=True)
    test_classsic_3d(show_viewer=True)