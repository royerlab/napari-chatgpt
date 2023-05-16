import os


def get_home_folder():
    # Get the home directory
    home_dir = os.path.expanduser('~')

    return home_dir


def get_or_create_folder_in_home(folder_name: str):
    home_folder = get_home_folder()

    # Create the path to the cache folder
    folder = os.path.join(home_folder, folder_name)

    # Check if the cache folder exists, and create it if it doesn't
    if not os.path.exists(folder):
        os.mkdir(folder)

    return folder
