import pytest

from napari_chatgpt.llm.api_keys.api_key_vault import (KeyVault, _decode64,
                                                       _encode64)


def test_b64_encode_decode():
    plain = "1234"
    encoded = _encode64(plain)
    decoded = _decode64(encoded)
    assert plain == decoded


def test_api_key_vault(tmp_path):
    api_key = "APIKEY123456789"

    key_vault = KeyVault("dummy", folder_path=str(tmp_path))

    key_vault.clear_key()

    assert not key_vault.is_key_present()

    encrypted_key = key_vault.write_api_key(api_key, "1234")

    assert encrypted_key

    assert key_vault.is_key_present()

    with pytest.raises(Exception):
        key_vault.read_api_key("12345")

    correct_api_key = key_vault.read_api_key("1234")

    assert correct_api_key == api_key
