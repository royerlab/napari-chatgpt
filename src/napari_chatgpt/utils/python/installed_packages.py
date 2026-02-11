"""Utilities for querying installed Python packages.

Provides functions to list installed packages (via pip and conda),
check whether a specific package is installed, and filter the list
to signal-processing-related packages.
"""

import importlib.util
import traceback
from functools import lru_cache
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as pkg_version

from napari_chatgpt.utils.python.relevant_libraries import (
    get_all_signal_processing_related_packages,
)


@lru_cache
def installed_package_list(
    clean_up: bool = True,
    version: bool = True,
    filter=get_all_signal_processing_related_packages(),
):
    """Return a deduplicated list of installed packages from pip and conda.

    Args:
        clean_up: If True, exclude AWS and internal library packages.
        version: If True, include version numbers (e.g., "numpy==1.24.0").
        filter: Iterable of package name substrings to keep. Only packages
            containing at least one of these substrings are included.
            Defaults to signal-processing-related packages.

    Returns:
        A deduplicated list of installed package names (with optional versions).
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
    """List packages installed via pip using ``importlib.metadata``.

    Args:
        version: If True, format entries as "name==version".

    Returns:
        List of package name strings, or an empty list on error.
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
        traceback.print_exc()
        return []


def conda_list(version: bool = False):
    """List packages installed via conda by invoking ``conda list``.

    Args:
        version: If True, format entries as "name==version".

    Returns:
        List of package name strings, or an empty list on error
        (e.g., if conda is not available).
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
        traceback.print_exc()
        return []


def is_package_installed(package_name: str):
    """Check whether a Python package is installed.

    Supports version-pinned names (e.g., "numpy==1.24.0"). When a version
    is specified, the installed version must match exactly.

    Args:
        package_name: Package name, optionally with "==version" suffix.

    Returns:
        True if the package is installed (and version matches if specified).
    """
    try:
        # Extract package name and version if provided
        version_required = None
        if "==" in package_name:
            package_name, version_required = package_name.split("==")

        # Check if the package is installed
        spec = importlib.util.find_spec(package_name)
        if spec is None:
            return False

        # If a version was provided, check it
        if version_required:
            installed_version = pkg_version(package_name)
            return installed_version == version_required

        return True

    except PackageNotFoundError:
        # The package is not installed
        return False
    except Exception as e:
        traceback.print_exc()
        return False
