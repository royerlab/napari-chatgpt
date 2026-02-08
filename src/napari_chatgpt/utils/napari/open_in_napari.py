import tempfile
import traceback
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from napari import Viewer


def open_in_napari(viewer: "Viewer", url: str, plugin: str = "napari") -> bool:
    try:
        viewer.open(url, plugin=plugin)
        return True
    except Exception:
        if open_zarr_in_napari(viewer, url):
            return True
        elif _open_imageio_in_napari(viewer, url):
            return True
        elif open_video_in_napari(viewer, url):
            return True
        else:
            return False


def open_video_in_napari(viewer: "Viewer", url: str):
    try:
        # First we check if it is a file that we can reasonably expect to open:
        if not (
            url.endswith("mp4")
            or url.endswith("mpg")
            or url.endswith("mov")
            or url.endswith("avi")
            or url.endswith("m4v")
        ):
            return False

        # temp folder:
        temp_folder = tempfile.gettempdir()

        # Download video file:
        from napari_chatgpt.utils.download.download_files import download_files

        file_paths = download_files(urls=[url], path=temp_folder)
        file_path = file_paths[0]

        # open video:
        import imageio.v3 as iio

        videodata = iio.imread(f"imageio:{file_path}", plugin="pyav")

        # Add to napari:
        viewer.add_image(videodata)

        return True

    except Exception:
        traceback.print_exc()
        return False


def _open_imageio_in_napari(viewer: "Viewer", url: str) -> bool:
    try:
        import imageio.v3 as imageio

        array = imageio.imread(url)
        viewer.add_image(array)

        return True

    except Exception:
        traceback.print_exc()
        return False


def open_zarr_in_napari(viewer: "Viewer", url: str) -> bool:
    if _open_ome_zarr_in_napari(viewer, url):
        return True
    elif _open_zarr_in_napari(viewer, url):
        return True
    else:
        return False


def _open_zarr_in_napari(viewer: "Viewer", url: str) -> bool:
    try:
        import zarr

        z = zarr.convenience.open(url, mode="r")

        viewer.add_image(z)

        return True

    except Exception:
        traceback.print_exc()
        return False


def _open_ome_zarr_in_napari(viewer: "Viewer", url: str) -> bool:
    try:
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

    except Exception:
        traceback.print_exc()
        return False
