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


import requests

import requests
import tempfile
import os

def download_file_stealth(url, file_path=None) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",  # Do Not Track Request Header
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

    response = requests.get(url, headers=headers, stream=True)

    if response.status_code == 200:
        if file_path is None:
            # Use a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            file_path = temp_file.name
            file_obj = temp_file
        else:
            # Use the specified file path
            file_obj = open(file_path, 'wb')

        with file_obj as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

        print(f"File downloaded: {file_path}")
        return file_path
    else:
        print(f"Failed to download file: status code {response.status_code}")
        return None


