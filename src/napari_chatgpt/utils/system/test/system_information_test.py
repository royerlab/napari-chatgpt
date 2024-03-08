from arbol import aprint

from napari_chatgpt.utils.system.information import system_info


def test_system_information():
    info = system_info(add_python_info=False)

    assert "Machine" in info
    assert "Version" in info
    assert "Platform" in info
    assert "System" in info


    print('')
    aprint(info)
