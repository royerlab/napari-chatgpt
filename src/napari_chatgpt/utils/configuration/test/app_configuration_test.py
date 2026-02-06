from napari_chatgpt.utils.configuration.app_configuration import AppConfiguration


def test_app_configuration(tmp_path, monkeypatch):
    # Redirect expanduser so config files go to tmp_path instead of home dir
    monkeypatch.setattr(
        "os.path.expanduser",
        lambda p: str(tmp_path / p.removeprefix("~/").removeprefix("~")),
    )
    # Clear singleton cache so our test gets a fresh instance
    AppConfiguration._instances.clear()

    default_config = {"test_key_2": "default_value"}

    config_1 = AppConfiguration("test_app_configuration", default_config=default_config)

    assert config_1["test_key_2"] == "default_value"
    config_1["test_key"] = "test_value"
    assert config_1["test_key"] == "test_value"
    config_1["test_key"] = "test_value2"
    assert config_1["test_key"] == "test_value2"

    # Clear singleton to force re-load from disk
    AppConfiguration._instances.clear()

    config_2 = AppConfiguration("test_app_configuration")
    assert config_2["test_key"] == "test_value2"
    assert config_2["test_key_2"] == "default_value"

    # Clean up singleton cache
    AppConfiguration._instances.clear()
