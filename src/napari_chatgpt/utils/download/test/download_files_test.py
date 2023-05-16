import os
import tempfile

from arbol import aprint

from napari_chatgpt.utils.download.download_files import download_files
from napari_chatgpt.utils.strings.extract_urls import extract_urls


def test_download_files():
    # Example string with urls:
    text = "Check out my website at https://www.example.com! " \
           "For more information, visit http://en.wikipedia.org/wiki/URL."

    # extract urls:
    urls = extract_urls(text)
    aprint(urls)

    # create files in temp directory:
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Download files:
        download_files(urls, tmp_dir)

        # Check if all downloaded files exist in the temporary directory
        for url in urls:
            file_name = url.split('/')[-1]
            file_path = os.path.join(tmp_dir, file_name)
            assert os.path.exists(file_path)
