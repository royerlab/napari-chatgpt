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


def test_singleton_no_reinit(tmp_path, monkeypatch):
    """Fix 9: singleton __init__ should not reset config."""
    monkeypatch.setattr(
        "os.path.expanduser",
        lambda p: str(tmp_path / p.removeprefix("~/").removeprefix("~")),
    )
    AppConfiguration._instances.clear()

    config = AppConfiguration("test_reinit", default_config={"key1": "val1"})
    config["runtime_key"] = "runtime_value"
    assert config["runtime_key"] == "runtime_value"

    # Get the "same" singleton again — __init__ should be skipped
    config2 = AppConfiguration("test_reinit", default_config={"key1": "val1"})
    assert config2 is config
    assert config2["runtime_key"] == "runtime_value"

    # Clean up
    AppConfiguration._instances.clear()
