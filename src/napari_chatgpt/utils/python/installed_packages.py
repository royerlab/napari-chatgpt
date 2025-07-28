from functools import lru_cache

from napari_chatgpt.utils.python.relevant_libraries import (
    get_all_signal_processing_related_packages,
)


@lru_cache
def installed_package_list(
    clean_up: bool = True,
    version: bool = True,
    filter=get_all_signal_processing_related_packages(),
):
    """
    Return a list of installed Python packages from both pip and conda environments, with optional filtering and version information.
    
    Parameters:
        clean_up (bool): If True, excludes packages containing "aws-" or "lib" in their names.
        version (bool): If True, includes package versions in the format "name==version".
        filter (list, optional): If provided, only packages containing any of the specified substrings are included.
    
    Returns:
        list: A deduplicated list of installed package names, optionally including version information.
    """
    package_list = pip_list(version=version) + conda_list(version=version)

    if clean_up:
        package_list = [pkg for pkg in package_list if not "aws-" in pkg]
        package_list = [pkg for pkg in package_list if not "lib" in pkg]

    if filter:
        package_list = [pkg for pkg in package_list if any(f in pkg for f in filter)]

    # Remove duplicates in list:
    package_list = list(set(package_list))

    return package_list


def pip_list(version: bool = False):
    """
    Retrieve a list of installed pip packages in the current Python environment.
    
    Parameters:
        version (bool): If True, includes package versions in the format "name==version"; otherwise, returns only package names.
    
    Returns:
        list: A list of installed package names or "name==version" strings. Returns an empty list if an error occurs.
    """
    try:
        import importlib.metadata as metadata

        # Get a list of installed packages
        if version:
            package_list = [
                f"{pkg.metadata['name']}=={pkg.metadata['version']}"
                for pkg in metadata.distributions()
            ]
        else:
            package_list = [pkg.metadata["name"] for pkg in metadata.distributions()]

        return package_list

    except Exception as e:
        print(traceback.format_exc())
        return []


def conda_list(version: bool = False):
    """
    Return a list of installed conda packages, optionally including version numbers.
    
    Parameters:
        version (bool): If True, each package is returned as "name==version"; otherwise, only the package name is returned.
    
    Returns:
        list: A list of installed conda package names, with or without version information.
    """
    try:
        import subprocess

        # Run the conda command to get a list of installed packages
        output = subprocess.check_output(["conda", "list"]).decode("utf-8").strip()

        # Split the output into lines and print the package names
        if version:
            package_list = [
                f"{line.split()[0]}=={line.split()[1]}"
                for line in output.split("\n")
                if not line.startswith("#")
            ]
        else:
            package_list = [
                line.split()[0]
                for line in output.split("\n")
                if not line.startswith("#")
            ]

        return package_list

    except Exception as e:
        print(traceback.format_exc())
        return []


import traceback
from pkgutil import find_loader
from importlib.metadata import version, PackageNotFoundError


def is_package_installed(package_name: str):
    """
    Check if a Python package is installed, optionally verifying a specific version.
    
    Parameters:
        package_name (str): The package name, optionally with a version specifier (e.g., "numpy==1.21.0").
    
    Returns:
        bool: True if the package (and version, if specified) is installed; otherwise, False.
    """
    try:
        # Extract package name and version if provided
        version_required = None
        if "==" in package_name:
            package_name, version_required = package_name.split("==")

        # Check if the package is installed
        loader = find_loader(package_name)
        if loader is None:
            return False

        # If a version was provided, check it
        if version_required:
            installed_version = version(package_name)
            return installed_version == version_required

        return True

    except PackageNotFoundError:
        # The package is not installed
        return False
    except Exception as e:
        traceback.print_exc()
        return False
