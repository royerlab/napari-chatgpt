import os
import urllib.request
from typing import List

from arbol import aprint, asection


def download_files(urls, path=None) -> List[str]:
    # Defaults to working directory:
    path = path or os.getcwd()

    filenames = []

    with asection("Downloading files:"):
        # Iterates through urls:
        for url in urls:
            # builds the filepath from the url:
            file_name = url.split('/')[-1]
            file_path = path + '/' + file_name

            # Downloads
            aprint(f'Downloading file at {url} to {file_path}...')
            urllib.request.urlretrieve(url, file_path)

            # Add filenames to list:
            filenames.append(file_name)

    return filenames
