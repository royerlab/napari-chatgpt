from arbol import aprint

from napari_chatgpt.utils.python.installed_packages import \
    installed_package_list, \
    is_package_installed


def test_installed_packages():
    package_list = installed_package_list()
    package_list_str = ', '.join(package_list)
    aprint(package_list_str)

    assert 'numpy' in package_list_str
    assert 'napari' in package_list_str


def test_is_package_installed():
    assert is_package_installed('numpy')
    assert not is_package_installed('grumpy')
