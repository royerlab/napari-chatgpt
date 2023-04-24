from arbol import aprint

from src.napari_chatgpt.utils.installed_packages import installed_package_list


def test_installed_packages():
    package_list = installed_package_list()
    package_list_str = ', '.join(package_list)
    aprint(package_list_str)
