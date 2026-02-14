from napari_chatgpt.omega_agent.tools.napari.delegated_code.tests.classic_test import (
    test_classic_2d,
    test_classic_3d,
)

if __name__ == "__main__":
    test_classic_2d(show_viewer=True)
    test_classic_3d(show_viewer=True)
