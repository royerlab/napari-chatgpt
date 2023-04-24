import traceback

import napari


def open_in_napari(viewer: napari.Viewer(), url: str) -> bool:
    if open_zarr_in_napari(viewer, url):
        return True
    elif _open_imageio_in_napari(viewer, url):
        return True
    else:
        return False


def _open_imageio_in_napari(viewer: napari.Viewer(), url: str) -> bool:
    try:
        import imageio.v3 as imageio

        array = imageio.imread(url)
        viewer.add_image(array)

        return True

    except:
        traceback.print_exc()
        return False


def open_zarr_in_napari(viewer: napari.Viewer(), url: str) -> bool:
    if _open_ome_zarr_in_napari(viewer, url):
        return True
    elif _open_zarr_in_napari(viewer, url):
        return True
    else:
        return False


def _open_zarr_in_napari(viewer: napari.Viewer(), url: str) -> bool:
    try:
        import zarr
        z = zarr.convenience.open(url, mode='r')

        viewer.add_image(z)

        return True

    except:
        traceback.print_exc()
        return False


def _open_ome_zarr_in_napari(viewer: napari.Viewer(), url: str) -> bool:
    try:
        import zarr
        from ome_zarr.io import parse_url
        from ome_zarr.reader import Reader

        # read the image data
        store = parse_url(url)

        # Open reader:
        reader = Reader(store)

        # nodes may include images, labels etc
        nodes = list(reader())

        # first node will be the image pixel data
        image_node = nodes[0]

        # Zarr array:
        z = image_node.data

        # Add to napari:
        viewer.add_image(z)

        return True

    except:
        traceback.print_exc()
        return False
