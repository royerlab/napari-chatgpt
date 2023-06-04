import napari
import numpy
from arbol import aprint
from skimage import data

from napari_chatgpt.utils.napari.napari_viewer_info import \
    get_viewer_layers_info
import napari
from skimage import data
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label
from skimage.morphology import closing, square, remove_small_objects

def test_napari_viewer_info():

    print('\n')

    # Instantiating Napari viewer headlessly:
    viewer = napari.Viewer(show=False)

    # IMAGE LAYER:
    cells = data.cells3d()[30, 1]  # grab some data
    viewer.add_image(cells, name='cells', colormap='magma')

    # LABELS LAYER:
    coins = data.coins()[50:-50, 50:-50]
    # apply threshold
    thresh = threshold_otsu(coins)
    bw = closing(coins > thresh, square(4))
    # remove artifacts connected to image border
    cleared = remove_small_objects(clear_border(bw), 20)
    # label image regions
    label_image = label(cleared)
    viewer.add_labels(label_image, name='segmentation')

    # LABELS LAYER:
    points = numpy.array([[100, 100], [200, 200], [300, 100]])
    viewer.add_points(points, size=30, name='points')

    # SHAPES LAYER:
    # create the list of polygons
    triangle = numpy.array([[11, 13], [111, 113], [22, 246]])
    person = numpy.array([[505, 60], [402, 71], [383, 42], [251, 95], [212, 59],
                       [131, 137], [126, 187], [191, 204], [171, 248],
                       [211, 260],
                       [273, 243], [264, 225], [430, 173], [512, 160]])
    building = numpy.array([[310, 382], [229, 381], [209, 401], [221, 411],
                         [258, 411], [300, 412], [306, 435], [268, 434],
                         [265, 454], [298, 461], [307, 461], [307, 507],
                         [349, 510], [352, 369], [330, 366], [330, 366]])
    polygons = [triangle, person, building]
    # add the polygons
    viewer.add_shapes(polygons, shape_type='polygon',
                                edge_width=5,
                                edge_color='coral',
                                face_color='royalblue',
                                name='some_shapes',)

    # SURFACE LAYER:
    vertices = numpy.array([[0, 0], [0, 20], [10, 0], [10, 10]])
    faces = numpy.array([[0, 1, 2], [1, 2, 3]])
    values = numpy.linspace(0, 1, len(vertices))
    surface = (vertices, faces, values)
    viewer.add_surface(surface,name='a_surface')  # add the surface

    # TRACK LAYER:
    tracks_data = [
        [1, 0, 236, 0],
        [1, 1, 236, 100],
        [1, 2, 236, 200],
        [1, 3, 236, 500],
        [1, 4, 236, 1000],
        [2, 0, 436, 0],
        [2, 1, 436, 100],
        [2, 2, 436, 200],
        [2, 3, 436, 500],
        [2, 4, 436, 1000],
        [3, 0, 636, 0],
        [3, 1, 636, 100],
        [3, 2, 636, 200],
        [3, 3, 636, 500],
        [3, 4, 636, 1000]
    ]
    viewer.add_tracks(tracks_data, name='my_tracks')

    # VECTORS LAYER:
    # create vector data
    n = 250
    vectors = numpy.zeros((n, 2, 2), dtype=numpy.float32)
    phi_space = numpy.linspace(0, 4 * numpy.pi, n)
    radius_space = numpy.linspace(0, 100, n)
    # assign x-y projection
    vectors[:, 1, 0] = radius_space * numpy.cos(phi_space)
    vectors[:, 1, 1] = radius_space * numpy.sin(phi_space)
    # assign x-y position
    vectors[:, 0] = vectors[:, 1] + 256
    # add the vectors
    vectors_layer = viewer.add_vectors(vectors, edge_width=3)

    # GET LAYER INFO FROM VIEWER:
    layers_info = get_viewer_layers_info(viewer)

    aprint(layers_info)

    assert len(layers_info) > 0
