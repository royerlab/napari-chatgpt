from napari_chatgpt.utils.qt.package_dialog import \
    install_packages_dialog_threadsafe, install_packages_dialog

if __name__ == '__main__':
    install_packages_dialog(packages=['a', 'b'])