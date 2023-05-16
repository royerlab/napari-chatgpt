import os

import requests
from tqdm import tqdm

from napari_chatgpt.utils.qt.download_file_qt import download_file_qt


def get_gpt4all_model(model_name: str = 'ggml-gpt4all-l13b-snoozy',
                      folder: str = None,
                      use_qt: bool = True):
    # By default this is where we store the models:
    if not folder:
        folder = os.path.join(os.path.expanduser("~"), '.gpt4all')

    # Create folder if it does not exist:
    os.makedirs(folder, exist_ok=True)

    # Filename:
    filename = f'{model_name}.bin'

    # Model filepath:
    file_path = os.path.join(folder, filename)

    # If file already downloaded, just return path:
    if os.path.exists(file_path):
        return file_path

    # Example model. Check https://github.com/nomic-ai/pygpt4all for the latest models.
    url = f'http://gpt4all.io/models/{filename}'

    if use_qt:
        download_file_qt(url, filename, folder)

    else:

        # send a GET request to the URL to download the file. Stream since it's large
        response = requests.get(url, stream=True)

        # Open the file in binary mode and write the contents of the response to it in chunks
        # This is a large file, so be prepared to wait.
        with open(file_path, 'wb') as f:
            for chunk in tqdm(response.iter_content(chunk_size=8192)):
                if chunk:
                    f.write(chunk)

    return file_path
