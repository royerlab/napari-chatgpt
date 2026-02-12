"""Utilities for locating and creating folders relative to the user's home directory."""

import os


def get_home_folder():
    """Return the absolute path to the user's home directory."""
    # Get the home directory
    home_dir = os.path.expanduser("~")

    return home_dir


def get_or_create_folder_in_home(folder_name: str):
    """Return the path to ``~/{folder_name}``, creating it if necessary.

    Args:
        folder_name: Name of the folder inside the home directory.

    Returns:
        Absolute path to the folder.
    """
    home_folder = get_home_folder()

    # Create the path to the cache folder
    folder = os.path.join(home_folder, folder_name)

    # Check if the cache folder exists, and create it if it doesn't
    if not os.path.exists(folder):
        os.mkdir(folder)

    return folder
