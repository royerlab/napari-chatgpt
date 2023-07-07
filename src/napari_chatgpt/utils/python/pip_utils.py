from typing import List

from arbol import aprint, asection
from napari_chatgpt.utils.python.conda_utils import conda_install

from napari_chatgpt.utils.python.installed_packages import is_package_installed


def pip_install(packages: List[str],
                ignore_obvious: bool = True,
                special_rules: bool = True) -> bool:
    if ignore_obvious:
        obvious_packages = ['numpy', 'napari', 'magicgui', 'scikit-image', 'scipy']
        aprint(
            f"Removing 'obvious' packages that should be already installed with Omega: {', '.join(obvious_packages)}")
        packages = [p for p in packages if
                    not p in obvious_packages]
        aprint(f'Packages left: {packages}')

    # Ensure it is a list:
    packages = list(packages)

    if special_rules:
        all_packages_str = ', '.join(packages)
        if 'opencv' in all_packages_str:
            packages.append('opencv-contrib-python')

        if 'cupy' in all_packages_str:
            packages.remove('cupy')
            # Special rules for CUPY and dependencies: https://docs.cupy.dev/en/stable/install.html
            conda_install(['cupy'], channel='conda-forge')

    # TODO: use conda to install some packages.

    try:
        with asection(f"Installing up to {len(packages)} packages with pip:"):
            for package in packages:
                pip_install_single_package(package)
        return True
    except CalledProcessError:
        traceback.print_exc()
        return False


import subprocess
import sys
import traceback
from subprocess import CalledProcessError


def pip_install_single_package(package: str,
                               upgrade: bool = False,
                               ignore_if_installed: bool = True):

    # Upgrade is a special case:
    if upgrade:
        ignore_if_installed = False

    # Check if we are on mac OSX
    if sys.platform == 'darwin':
        aprint(f"Detected OSX!")
        # Check if we are on M1:
        if 'arm64' in sys.version.lower():
            aprint(f"Detected M1 chip!")
            # Install tensorflow_macos:
            if package == 'tensorflow':
                aprint(f"Substituting tensorflow for tensorflow-macos!")
                package = 'tensorflow-macos'
            # Install tensorflow_macos:
            if package == 'tensorflow-gpu':
                aprint(f"Substituting tensorflow-gpu for tensorflow-metal!")
                package = 'tensorflow-metal'

    with asection(f"Pip installing package: {package}"):

        if ignore_if_installed and is_package_installed(package):
            aprint(f'Package {package} is already installed!')
        else:
            command = [sys.executable, "-m", "pip", "install", package]
            if upgrade:
                aprint(f"Upgrade requested!")
                command.append("--upgrade")

            subprocess.check_call(command)

            aprint(f"Installed!")


def pip_uninstall(list_of_packages: List[str]) -> bool:

    error_occurred = False

    with asection(f"Installing up to {len(list_of_packages)} packages with pip:"):
        for package in list_of_packages:

            if not is_package_installed(package):
                aprint(f'Package {package} is not installed!')
            else:
                try:
                    aprint(f"removing: {package}")
                    process = subprocess.run(f"pip uninstall -y {package}", check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if process.returncode != 0:
                        print(f"An error occurred while uninstalling {package}. Error: {process.stderr.decode('utf-8')}")
                        error_occurred = True
                except subprocess.CalledProcessError as e:
                    print(f"An error occurred while uninstalling {package}. Error: {e}")
                    error_occurred = True

    return not error_occurred
