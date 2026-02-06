import subprocess

from arbol import aprint, asection

from napari_chatgpt.utils.python.installed_packages import is_package_installed


def conda_install(list_of_packages: list[str], channel: str | None = None) -> bool:
    # Ensure it is a list and remove duplicates:
    list_of_packages = list(set(list_of_packages))

    error_occurred = False

    with asection(f"Installing up to {len(list_of_packages)} packages with conda:"):
        for package in list_of_packages:

            if is_package_installed(package):
                aprint(f"Package {package} is already installed!")
            else:
                # Build command as list to avoid shell injection
                cmd = ["conda", "install", "-y"]
                if channel:
                    cmd.extend(["-c", channel])
                cmd.append(package)

                try:
                    aprint(f"Conda installing package: {package}")
                    process = subprocess.run(
                        cmd,
                        check=True,
                        capture_output=True,
                    )
                    if process.returncode != 0:
                        aprint(
                            f"An error occurred while installing {package}. Error: {process.stderr.decode('utf-8')}"
                        )
                        error_occurred = True

                except subprocess.CalledProcessError as e:
                    aprint(f"An error occurred while installing {package}. Error: {e}")
                    error_occurred = True

    return not error_occurred


def conda_uninstall(list_of_packages: list[str]) -> bool:
    error_occurred = False

    with asection(f"Uninstalling up to {len(list_of_packages)} packages with conda:"):
        for package in list_of_packages:

            if not is_package_installed(package):
                aprint(f"Package {package} is not installed!")
            else:
                # Build command as list to avoid shell injection
                cmd = ["conda", "uninstall", "-y", package]

                try:
                    aprint(f"removing: {package}")
                    process = subprocess.run(
                        cmd,
                        check=True,
                        capture_output=True,
                    )
                    if process.returncode != 0:
                        aprint(
                            f"An error occurred while uninstalling {package}. Error: {process.stderr.decode('utf-8')}"
                        )
                        error_occurred = True
                except subprocess.CalledProcessError as e:
                    aprint(
                        f"An error occurred while uninstalling {package}. Error: {e}"
                    )
                    error_occurred = True

    return not error_occurred
