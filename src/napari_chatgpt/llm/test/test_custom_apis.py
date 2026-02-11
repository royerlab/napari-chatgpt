"""Tests for custom API endpoint registration and GitHub Models detection."""

import os
from unittest.mock import MagicMock, patch

from napari_chatgpt.llm.litemind_api import (
    _build_custom_apis,
    _register_api,
)

# Patch target for AppConfiguration (imported locally)
_CONFIG_PATCH = (
    "napari_chatgpt.utils.configuration" ".app_configuration.AppConfiguration"
)


def _mock_config(items=None):
    """Create a mock AppConfiguration that supports [] access."""
    data = items or {}
    mock = MagicMock()
    mock.__getitem__ = MagicMock(side_effect=lambda key: data.get(key))
    mock.get = MagicMock(side_effect=lambda key, default=None: data.get(key, default))
    return mock


class TestRegisterApi:
    """Tests for the _register_api helper."""

    def test_registers_models(self):
        combined = MagicMock()
        combined.model_to_api = {}
        combined.apis = []

        api = MagicMock()
        api.list_models.return_value = ["model-a", "model-b"]

        result = _register_api(combined, api)
        assert result is True
        assert "model-a" in combined.model_to_api
        assert "model-b" in combined.model_to_api
        assert api in combined.apis

    def test_skips_empty_models(self):
        combined = MagicMock()
        combined.model_to_api = {}
        combined.apis = []

        api = MagicMock()
        api.list_models.return_value = []

        result = _register_api(combined, api)
        assert result is False
        assert len(combined.apis) == 0

    def test_does_not_overwrite_existing(self):
        existing_api = MagicMock()
        combined = MagicMock()
        combined.model_to_api = {"model-a": existing_api}
        combined.apis = [existing_api]

        new_api = MagicMock()
        new_api.list_models.return_value = ["model-a", "model-b"]

        _register_api(combined, new_api)
        assert combined.model_to_api["model-a"] is existing_api
        assert combined.model_to_api["model-b"] is new_api

    def test_handles_exception(self):
        combined = MagicMock()
        combined.model_to_api = {}
        combined.apis = []

        api = MagicMock()
        api.list_models.side_effect = Exception("connection failed")
        api.__class__.__name__ = "TestApi"

        result = _register_api(combined, api)
        assert result is False


class TestBuildCustomApis:
    """Tests for _build_custom_apis with mocked config and env."""

    @patch(_CONFIG_PATCH)
    def test_no_custom_endpoints(self, mock_config_cls):
        mock_config_cls.return_value = _mock_config()

        combined = MagicMock()
        combined.model_to_api = {}
        combined.apis = []

        with patch.dict(os.environ, {}, clear=True):
            _build_custom_apis(combined)
        assert len(combined.apis) == 0

    @patch(_CONFIG_PATCH)
    def test_missing_base_url_skipped(self, mock_config_cls):
        mock_config_cls.return_value = _mock_config(
            {
                "custom_endpoints": [{"name": "bad", "api_key_env": "KEY"}],
            }
        )

        combined = MagicMock()
        combined.model_to_api = {}
        combined.apis = []

        with patch.dict(os.environ, {}, clear=True):
            _build_custom_apis(combined)
        assert len(combined.apis) == 0

    @patch(_CONFIG_PATCH)
    def test_github_token_detected(self, mock_config_cls):
        mock_config_cls.return_value = _mock_config()

        mock_api = MagicMock()
        mock_api.list_models.return_value = ["gpt-4o"]

        combined = MagicMock()
        combined.model_to_api = {}
        combined.apis = []

        env = {"GITHUB_TOKEN": "ghp_test123"}
        with patch.dict(os.environ, env, clear=True):
            with patch(
                "litemind.apis.providers.openai.openai_api.OpenAIApi",
                return_value=mock_api,
            ) as patched:
                _build_custom_apis(combined)

                patched.assert_called_with(
                    api_key="ghp_test123",
                    base_url="https://models.inference.ai.azure.com",
                )

    @patch(_CONFIG_PATCH)
    def test_no_github_token(self, mock_config_cls):
        mock_config_cls.return_value = _mock_config()

        combined = MagicMock()
        combined.model_to_api = {}
        combined.apis = []

        with patch.dict(os.environ, {}, clear=True):
            _build_custom_apis(combined)
        assert len(combined.apis) == 0
