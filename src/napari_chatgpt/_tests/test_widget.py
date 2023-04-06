import numpy as np

from napari_chatgpt import ExampleQWidget, example_magic_widget


# make_napari_viewer is a pytest fixture that returns a napari viewer object
# capsys is a pytest fixture that captures stdout and stderr output streams
def test_example_q_widget(make_napari_viewer, capsys):
    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()
    viewer.add_image(np.random.random((100, 100)))

    # create our widget, passing in the viewer
    my_widget = ExampleQWidget(viewer)

    # call our widget method
    my_widget._on_click()

    # read captured output and check that it's as we expected
    captured = capsys.readouterr()
    assert captured.out == "napari has 1 layers\n"


def test_example_magic_widget(make_napari_viewer, capsys):
    viewer = make_napari_viewer()
    layer = viewer.add_image(np.random.random((100, 100)))

    # this time, our widget will be a MagicFactory or FunctionGui instance
    my_widget = example_magic_widget()

    # if we "call" this object, it'll execute our function
    my_widget(viewer.layers[0])

    # read captured output and check that it's as we expected
    captured = capsys.readouterr()
    assert captured.out == f"you have selected {layer}\n"
