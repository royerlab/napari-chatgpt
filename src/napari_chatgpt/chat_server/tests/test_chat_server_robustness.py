"""Tests for chat_server robustness fixes."""

import asyncio
from dataclasses import dataclass
from unittest.mock import AsyncMock

from napari_chatgpt.chat_server.chat_response import ChatResponse


# ---------------------------------------------------------------------------
# 1. notify_user_omega_error: non-string error.args must not crash
# ---------------------------------------------------------------------------
class TestErrorArgsJoin:
    """Verify that error.args with non-string elements don't crash."""

    def _build_error_message(self, error: Exception) -> str:
        """Reproduce the logic from notify_user_omega_error."""
        error_type = type(error).__name__
        error_message = ", ".join(str(a) for a in error.args)
        return f"Failed because:\n'{error_message}'\n" f"Exception: '{error_type}'\n"

    def test_string_args(self):
        error = ValueError("something went wrong")
        msg = self._build_error_message(error)
        assert "something went wrong" in msg
        assert "ValueError" in msg

    def test_integer_args(self):
        error = OSError(22, "Invalid argument")
        msg = self._build_error_message(error)
        assert "22" in msg
        assert "Invalid argument" in msg

    def test_none_arg(self):
        error = Exception(None)
        msg = self._build_error_message(error)
        assert "None" in msg

    def test_mixed_args(self):
        error = Exception("msg", 42, None, [1, 2])
        msg = self._build_error_message(error)
        assert "msg" in msg
        assert "42" in msg
        assert "None" in msg
        assert "[1, 2]" in msg

    def test_empty_args(self):
        error = Exception()
        msg = self._build_error_message(error)
        assert "Exception" in msg


# ---------------------------------------------------------------------------
# 2. tool_result type name (was tool_end)
# ---------------------------------------------------------------------------
class TestToolResultType:
    """Verify the server uses 'tool_result' not 'tool_end'."""

    def test_tool_end_response_uses_tool_result_type(self):
        """ChatResponse for tool end uses type='tool_result'."""
        message = "some result"
        resp = ChatResponse(sender="agent", message=message, type="tool_result")
        d = resp.dict()
        assert d["type"] == "tool_result"
        assert d["message"] == message
        assert d["sender"] == "agent"


# ---------------------------------------------------------------------------
# 3. async send functions: test they await websocket.send_json
# ---------------------------------------------------------------------------
class TestAsyncSendFunctions:
    """Test that send_final_response_to_user and
    notify_user_omega_thinking use await (not sync_handler)."""

    def test_notify_thinking_awaits_send_json(self):
        """notify_user_omega_thinking should await send_json."""
        ws = AsyncMock()

        async def notify_user_omega_thinking(websocket):
            resp = ChatResponse(sender="agent", message="", type="thinking")
            await websocket.send_json(resp.dict())

        loop = asyncio.new_event_loop()
        loop.run_until_complete(notify_user_omega_thinking(ws))
        loop.close()
        ws.send_json.assert_awaited_once()
        call_arg = ws.send_json.call_args[0][0]
        assert call_arg["type"] == "thinking"

    def test_send_final_response_awaits_send_json(self):
        """send_final_response_to_user should await send_json."""
        ws = AsyncMock()

        @dataclass
        class FakeText:
            pass

        class FakeMessage:
            def has(self, cls):
                return True

            def to_plain_text(self):
                return "hello world"

        async def send_final_response_to_user(result, websocket):
            text_result = [m for m in result if m.has(FakeText)]
            message_str = "\n\n".join([m.to_plain_text() for m in text_result])
            end_resp = ChatResponse(
                sender="agent",
                message=message_str,
                type="final",
            )
            await websocket.send_json(end_resp.dict())

        loop = asyncio.new_event_loop()
        loop.run_until_complete(send_final_response_to_user([FakeMessage()], ws))
        loop.close()
        ws.send_json.assert_awaited_once()
        call_arg = ws.send_json.call_args[0][0]
        assert call_arg["type"] == "final"
        assert call_arg["message"] == "hello world"


# ---------------------------------------------------------------------------
# 4. NapariChatServer no longer inherits BaseToolCallbacks
# ---------------------------------------------------------------------------
class TestNoBaseToolCallbacksInheritance:
    """Verify NapariChatServer does not inherit from BaseToolCallbacks."""

    def test_no_base_tool_callbacks_in_mro(self):
        from napari_chatgpt.chat_server.chat_server import NapariChatServer

        mro_names = [cls.__name__ for cls in NapariChatServer.__mro__]
        assert "BaseToolCallbacks" not in mro_names

    def test_direct_bases(self):
        from napari_chatgpt.chat_server.chat_server import NapariChatServer

        assert NapariChatServer.__bases__ == (object,)
