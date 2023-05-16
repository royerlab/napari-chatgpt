import os
import tempfile
import traceback


def open_in_napari(viewer: "Viewer", url: str) -> bool:
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
        # First we check if it is a file that we can resonable expect to open:
        if not (url.endswith('mp4') or url.endswith('mpg') or url.endswith(
                'mov') or url.endswith('avi') or url.endswith('m4v')):
            return False

        # temp folder:
        temp_folder = tempfile.gettempdir()

        # Download video file:
        from napari_chatgpt.utils.download.download_files import download_files
        files = download_files(urls=[url], path=temp_folder)
        file = files[0]

        # make full path:
        file_path = os.path.join(temp_folder, file)

        # open video:
        from skvideo.io import vread
        videodata = vread(file_path)

        # Add to napari:
        viewer.add_image(videodata)

        return True

    except:
        traceback.print_exc()
        return False


def _open_imageio_in_napari(viewer: "Viewer", url: str) -> bool:
    try:
        import imageio.v3 as imageio

        array = imageio.imread(url)
        viewer.add_image(array)

        return True

    except:
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
        z = zarr.convenience.open(url, mode='r')

        viewer.add_image(z)

        return True

    except:
        traceback.print_exc()
        return False


def _open_ome_zarr_in_napari(viewer: "Viewer", url: str) -> bool:
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
