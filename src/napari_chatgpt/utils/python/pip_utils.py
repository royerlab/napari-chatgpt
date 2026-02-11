"""Pip package management utilities with special-case handling.

Provides functions to install and uninstall Python packages via pip, with
support for package substitutions (e.g., stardist -> napari-stardist),
conda-forge fallbacks, macOS/M1 TensorFlow substitutions, and user
permission dialogs.
"""

from arbol import aprint, asection

from napari_chatgpt.utils.python.conda_utils import conda_install
from napari_chatgpt.utils.python.installed_packages import is_package_installed
from napari_chatgpt.utils.qt.package_dialog import install_packages_dialog_threadsafe

___included_packages = ["numpy", "napari", "magicgui", "scikit-image", "scipy"]

___extra_packages = {"opencv": ["opencv-contrib-python"]}

___pip_substitutions = {
    "stardist": ["napari-stardist"],
    "cellpose": ["cellpose-napari"],
}

___conda_forge_substitutions = {"cupy": ["cupy"]}


# Special rules for CUPY and dependencies: https://docs.cupy.dev/en/stable/install.html


def pip_install(
    packages: list[str],
    included: bool = True,
    special_rules: bool = True,
    skip_if_installed: bool = True,
    ask_permission: bool = True,
) -> str:
    """Install packages using pip with special-case handling.

    Applies package substitutions, removes already-included Omega packages,
    skips already-installed packages, and optionally prompts the user for
    permission before installing.

    Args:
        packages: List of package names to install.
        included: If True, remove packages already bundled with Omega.
        special_rules: If True, apply substitution and conda-forge rules.
        skip_if_installed: If True, skip already-installed packages.
        ask_permission: If True, show a dialog asking the user for permission.

    Returns:
        A message string describing the installation results.
    """

    message = ""

    if included:
        included_packages = ___included_packages
        aprint(
            f"Removing 'included' packages that should be already installed with Omega: {', '.join(included_packages)}"
        )
        packages = [p for p in packages if not p in included_packages]
        aprint(f"Packages left: {packages}")
        message += f"Removing 'included' packages that should be already installed with Omega: {', '.join(included_packages)}\n"

    # Ensure it is a list and remove duplicates:
    packages = list(set(packages))

    if special_rules:
        all_packages_str = ", ".join(packages)

        # Check for extra packages:
        for package, extras in ___extra_packages.items():
            if package in all_packages_str:
                for extra in extras:
                    packages.append(extra)
                    message += f"Adding '{extra}' to the list of packages to install.\n"

        # Check for substitutions:
        for package, substitutions in ___pip_substitutions.items():
            if package in all_packages_str:
                packages.remove(package)
                for substitute in substitutions:
                    packages.append(substitute)
                    message += (
                        f"Installing '{substitute}' with pip instead of '{package}'.\n"
                    )

        # Check for conda-forge substitutions:
        for package, substitutions in ___conda_forge_substitutions.items():
            if package in all_packages_str:
                packages.remove(package)
                conda_install(substitutions, channel="conda-forge")
                message += f"Installing '{','.join(substitutions)}' with conda-forge instead of '{package}'.\n"

    # TODO: use conda to install some packages.

    if skip_if_installed:
        # List of already installed packages:
        already_installed_packages = [p for p in packages if is_package_installed(p)]

        # remove packages that are already installed:
        packages = [p for p in packages if not is_package_installed(p)]

        message += f"Removing packages that are already installed: {', '.join(already_installed_packages)}\n"

    if len(packages) > 0:
        try:
            response = not ask_permission or install_packages_dialog_threadsafe(
                packages=packages
            )

            if response:
                aprint(f"User accepted to install packages!")
                message += f"User accepted to install packages: {', '.join(packages)}\n"
                with asection(f"Installing up to {len(packages)} packages with pip:"):
                    for package in packages:
                        message += pip_install_single_package(package=package)
                        message += "\n"

            else:
                message += f"User refused to install packages!\n"

            aprint(message)
            return message

        except CalledProcessError as e:
            traceback.print_exc()
            # return error message:
            return f"{message}\nError: {type(e).__name__} with message: '{str(e)}' occurred while trying to install these packages: '{','.join(packages)}'.\n"

    else:
        message = f"No packages to install!\n"
        return message


import subprocess
import sys
import traceback
from subprocess import CalledProcessError


def pip_install_single_package(
    package: str, upgrade: bool = False, skip_if_installed: bool = True
) -> str:
    """Install a single package via pip.

    Handles macOS/M1 TensorFlow substitutions automatically. When upgrade
    is True, skip_if_installed is forced to False.

    Args:
        package: Package name to install.
        upgrade: If True, pass --upgrade to pip and reinstall even if present.
        skip_if_installed: If True, skip if the package is already installed.

    Returns:
        A message string indicating success or failure.
    """
    # Upgrade is a special case:
    if upgrade:
        skip_if_installed = False

    # Check if we are on mac OSX
    if sys.platform == "darwin":
        aprint(f"Detected OSX!")
        # Check if we are on M1:
        if "arm64" in sys.version.lower():
            aprint(f"Detected M1 chip!")
            # Install tensorflow_macos:
            if package == "tensorflow":
                aprint(f"Substituting tensorflow for tensorflow-macos!")
                package = "tensorflow-macos"
            # Install tensorflow_macos:
            if package == "tensorflow-gpu":
                aprint(f"Substituting tensorflow-gpu for tensorflow-metal!")
                package = "tensorflow-metal"

    with asection(f"Pip installing package: {package}"):

        if skip_if_installed and is_package_installed(package):
            message = f"Package {package} is already installed!\n"
        else:
            command = [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--no-cache-dir",
                "-I",
                package,
            ]
            if upgrade:
                aprint(f"Upgrade requested!")
                command.append("--upgrade")

            # Running the command and capturing the output
            result = subprocess.run(command, capture_output=True, text=True)

            # Handling the captured output
            if result.returncode == 0:
                message = f"Installed!\n{result.stdout}\n"
            else:
                message = f"Error occurred:\n{result.stderr}\n"

        aprint(message)
        return message


def pip_uninstall(list_of_packages: list[str]) -> bool:
    """Uninstall packages using pip, skipping packages not installed.

    Args:
        list_of_packages: Package names to uninstall.

    Returns:
        True if all uninstallations succeeded, False if any errors occurred.
    """
    error_occurred = False

    # Ensure it is a list and remove duplicates:
    list_of_packages = list(set(list_of_packages))

    with asection(f"Installing up to {len(list_of_packages)} packages with pip:"):
        for package in list_of_packages:

            if not is_package_installed(package):
                aprint(f"Package {package} is not installed!")
            else:
                try:
                    aprint(f"removing: {package}")
                    process = subprocess.run(
                        [sys.executable, "-m", "pip", "uninstall", "-y", package],
                        check=True,
                        capture_output=True,
                    )
                    if process.returncode != 0:
                        print(
                            f"An error occurred while uninstalling {package}. Error: {process.stderr.decode('utf-8')}"
                        )
                        error_occurred = True
                except subprocess.CalledProcessError as e:
                    print(f"An error occurred while uninstalling {package}. Error: {e}")
                    error_occurred = True

    return not error_occurred
