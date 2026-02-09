"""Tests for TokenCounterCallback and estimate_tokens."""

from unittest.mock import MagicMock

from napari_chatgpt.llm.token_counter_callback import (
    TokenCounterCallback,
    estimate_tokens,
)


class TestEstimateTokens:
    """Tests for the estimate_tokens heuristic."""

    def test_empty_string(self):
        assert estimate_tokens("") == 0

    def test_none_like_empty(self):
        assert estimate_tokens("") == 0

    def test_single_word(self):
        result = estimate_tokens("hello")
        assert result >= 1

    def test_typical_sentence(self):
        text = "The quick brown fox jumps over the lazy dog"
        result = estimate_tokens(text)
        # 9 words * 1.3 = 11.7 -> 11
        assert result == 11

    def test_long_text(self):
        text = " ".join(["word"] * 100)
        result = estimate_tokens(text)
        assert result == 130  # 100 * 1.3


class TestTokenCounterCallback:
    """Tests for the TokenCounterCallback class."""

    def _make_message(self, text: str):
        msg = MagicMock()
        msg.to_plain_text.return_value = text
        return msg

    def test_initial_state(self):
        counter = TokenCounterCallback()
        assert counter.total_tokens == 0

    def test_single_call(self):
        counter = TokenCounterCallback()
        msgs = [self._make_message("hello world")]
        response = self._make_message("goodbye world")
        counter.on_text_generation(msgs, response)
        # "hello world" -> 2 words * 1.3 = 2.6 -> 2
        # "goodbye world" -> 2 words * 1.3 = 2.6 -> 2
        assert counter.total_tokens == 4

    def test_accumulates_across_calls(self):
        counter = TokenCounterCallback()
        msg1 = [self._make_message("one two three")]
        resp1 = self._make_message("four five")
        counter.on_text_generation(msg1, resp1)
        first = counter.total_tokens

        msg2 = [self._make_message("six seven")]
        resp2 = self._make_message("eight")
        counter.on_text_generation(msg2, resp2)
        assert counter.total_tokens > first

    def test_multiple_messages_in_single_call(self):
        counter = TokenCounterCallback()
        msgs = [
            self._make_message("system prompt here"),
            self._make_message("user question"),
        ]
        response = self._make_message("answer")
        counter.on_text_generation(msgs, response)
        assert counter.total_tokens > 0

    def test_reset(self):
        counter = TokenCounterCallback()
        msgs = [self._make_message("hello world")]
        response = self._make_message("goodbye")
        counter.on_text_generation(msgs, response)
        assert counter.total_tokens > 0
        counter.reset()
        assert counter.total_tokens == 0

    def test_response_as_list(self):
        """Response can be a List[Message] from CombinedApi.generate_text."""
        counter = TokenCounterCallback()
        msgs = [self._make_message("hello world")]
        response = [
            self._make_message("goodbye world"),
            self._make_message("extra message"),
        ]
        counter.on_text_generation(msgs, response)
        # "hello world" -> 2, "goodbye world" -> 2, "extra message" -> 2
        assert counter.total_tokens == 6

    def test_empty_messages(self):
        counter = TokenCounterCallback()
        msgs = [self._make_message("")]
        response = self._make_message("")
        counter.on_text_generation(msgs, response)
        assert counter.total_tokens == 0
