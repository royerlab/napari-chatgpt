import subprocess
from typing import List

from arbol import asection, aprint

from napari_chatgpt.utils.python.installed_packages import is_package_installed


def conda_install(list_of_packages: List[str], channel:str = None) -> bool:
    base_command = "conda install -y"

    if channel:
        base_command += f" -c {channel}"

    error_occurred = False

    with asection(f"Installing up to {len(list_of_packages)} packages with conda:"):
        for package in list_of_packages:

            if is_package_installed(package):
                aprint(f'Package {package} is already installed!')
            else:
                command = f"{base_command} {package}"
                try:
                    aprint(f"Pip installing package: {package}")
                    process = subprocess.run(command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if process.returncode != 0:
                        aprint(f"An error occurred while installing {package}. Error: {process.stderr.decode('utf-8')}")
                        error_occurred = True

                except subprocess.CalledProcessError as e:
                    aprint(f"An error occurred while installing {package}. Error: {e}")
                    error_occurred = True

    return not error_occurred


def conda_uninstall(list_of_packages):
    base_command = "conda uninstall -y"

    error_occurred = False

    with asection(f"Installing up to {len(list_of_packages)} packages with conda:"):
        for package in list_of_packages:

            if not is_package_installed(package):
                aprint(f'Package {package} is not installed!')
            else:

                command = f"{base_command} {package}"
                try:
                    aprint(f"removing: {package}")
                    process = subprocess.run(command, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if process.returncode != 0:
                        aprint(f"An error occurred while uninstalling {package}. Error: {process.stderr.decode('utf-8')}")
                        error_occurred = True
                except subprocess.CalledProcessError as e:
                    aprint(f"An error occurred while uninstalling {package}. Error: {e}")
                    error_occurred = True

    return not error_occurred