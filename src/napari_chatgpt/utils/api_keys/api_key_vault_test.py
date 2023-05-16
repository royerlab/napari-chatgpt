from napari_chatgpt.utils.api_keys.api_key_vault import KeyVault, _encode64, \
    _decode64


def test_b64_encode_decode():
    plain = '1234'
    encoded = _encode64(plain)
    decoded = _decode64(encoded)
    assert plain == decoded


def test_api_key_vault():
    api_key = 'APIKEY123456789'

    key_vault = KeyVault('dummy')

    key_vault.clear_key()

    assert not key_vault.is_key_present()

    encrypted_key = key_vault.write_api_key(api_key, '1234')
    print(encrypted_key)

    assert encrypted_key

    assert key_vault.is_key_present()

    try:
        wrong_api_key = key_vault.read_api_key('12345')
        assert not wrong_api_key == api_key
        assert False

    except Exception:
        assert True

    correct_api_key = key_vault.read_api_key('1234')
    print(correct_api_key)

    assert correct_api_key == api_key
