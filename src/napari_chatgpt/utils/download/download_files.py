"""File download utilities with browser-like HTTP headers."""

import os
import tempfile
import urllib.parse

import requests
from arbol import aprint, asection

_DOWNLOAD_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml," "application/xml;q=0.9,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.5",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}


def _download_file(url, file_path) -> str:
    """Download a single file using proper HTTP headers."""
    response = requests.get(url, headers=_DOWNLOAD_HEADERS, stream=True, timeout=60)
    response.raise_for_status()

    with open(file_path, "wb") as f:
        for chunk in response.iter_content(8192):
            f.write(chunk)

    return file_path


def download_files(urls, path=None) -> list[str]:
    """Download multiple files from URLs to a local directory.

    Args:
        urls: Iterable of URLs to download.
        path: Destination directory. Defaults to the current working directory.

    Returns:
        List of absolute file paths for the downloaded files.
    """
    # Defaults to working directory:
    path = path or os.getcwd()

    file_paths = []

    with asection("Downloading files:"):
        # Iterates through urls:
        for url in urls:
            # Extract filename from URL using proper URL parsing:
            parsed = urllib.parse.urlparse(url)
            file_name = os.path.basename(parsed.path) or "downloaded_file"

            # Build the full file path:
            file_path = os.path.join(path, file_name)

            # Download:
            aprint(f"Downloading file at {url} to {file_path}...")
            _download_file(url, file_path)

            # Add full file paths to list:
            file_paths.append(file_path)

    return file_paths


def download_file_stealth(url, file_path=None) -> str:
    """Download a file, optionally to a temporary location.

    Args:
        url: URL to download.
        file_path: Destination path. If ``None``, a temporary file is created.

    Returns:
        Path to the downloaded file, or ``None`` on failure.
    """
    response = requests.get(url, headers=_DOWNLOAD_HEADERS, stream=True, timeout=60)

    if response.status_code == 200:
        if file_path is None:
            # Use a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            file_path = temp_file.name
            file_obj = temp_file
        else:
            # Use the specified file path
            file_obj = open(file_path, "wb")

        with file_obj as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)

        aprint(f"File downloaded: {file_path}")
        return file_path
    else:
        aprint(f"Failed to download file: " f"status code {response.status_code}")
        return None
