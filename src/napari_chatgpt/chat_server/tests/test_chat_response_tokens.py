"""Tests for ChatResponse token tracking fields."""

from napari_chatgpt.chat_server.chat_response import ChatResponse


class TestChatResponseTokens:
    """Verify ChatResponse includes token fields."""

    def test_default_values(self):
        resp = ChatResponse(sender="agent", message="hi", type="final")
        assert resp.tokens == 0
        assert resp.total_tokens == 0

    def test_dict_includes_token_fields(self):
        resp = ChatResponse(
            sender="agent",
            message="hi",
            type="final",
            tokens=100,
            total_tokens=500,
        )
        d = resp.dict()
        assert d["tokens"] == 100
        assert d["total_tokens"] == 500

    def test_dict_has_all_keys(self):
        resp = ChatResponse()
        d = resp.dict()
        expected_keys = {"sender", "message", "type", "tokens", "total_tokens"}
        assert set(d.keys()) == expected_keys
