import numpy as np

from napari_chatgpt import OmegaQWidget


# make_napari_viewer is a pytest fixture that returns a napari viewer object
# capsys is a pytest fixture that captures stdout and stderr output streams
def test_omega_q_widget(make_napari_viewer, capsys):
    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()
    viewer.add_image(np.random.random((100, 100)))

    # No testing of UI elements yet!
    #
    # # create our widget, passing in the viewer
    # my_widget = OmegaQWidget(viewer)
    #
    # # # call our widget method
    # # my_widget._on_click()
    # #
    # # # read captured output and check that it's as we expected
    # # captured = capsys.readouterr()
    # # assert 'Omega' in captured.out
