"""
Tests for the provider-agnostic LLM query generator.

Covers provider/key/model resolution (auto / anthropic / gemini / none) and the
Anthropic backend with a mocked SDK. The Gemini backend and JSON parsing are
covered in tests/test_broll_relevance.py; these tests focus on the multi-provider
plumbing added on top. All tests are offline.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, patch

from screenwrite.parsing.query_generator import QueryGenerator
from screenwrite.config import DEFAULT_ANTHROPIC_MODEL


class TestProviderResolution(unittest.TestCase):
    """Resolution of (provider, api_key, model) from args and environment."""

    def test_no_keys_unavailable(self):
        with patch.dict(os.environ, {}, clear=True):
            gen = QueryGenerator()
            self.assertFalse(gen.is_available())

    def test_explicit_key_defaults_to_gemini(self):
        # Historical behavior: an explicitly passed key uses Gemini.
        with patch.dict(os.environ, {}, clear=True):
            gen = QueryGenerator(api_key="real-key")
            self.assertTrue(gen.is_available())
            self.assertEqual(gen.provider, "gemini")

    def test_auto_prefers_anthropic(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "a-key",
                                     "GEMINI_API_KEY": "g-key"}, clear=True):
            gen = QueryGenerator()
            self.assertEqual(gen.provider, "anthropic")
            self.assertEqual(gen.api_key, "a-key")
            self.assertEqual(gen.model, DEFAULT_ANTHROPIC_MODEL)

    def test_auto_falls_back_to_gemini(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "g-key"}, clear=True):
            gen = QueryGenerator()
            self.assertEqual(gen.provider, "gemini")
            self.assertEqual(gen.api_key, "g-key")

    def test_provider_env_pins_choice(self):
        # Pinned to gemini but only an anthropic key exists -> unavailable.
        with patch.dict(os.environ, {"BROLL_LLM_PROVIDER": "gemini",
                                     "ANTHROPIC_API_KEY": "a-key"}, clear=True):
            gen = QueryGenerator()
            self.assertEqual(gen.provider, "gemini")
            self.assertFalse(gen.is_available())

    def test_provider_none_disables(self):
        with patch.dict(os.environ, {"BROLL_LLM_PROVIDER": "none",
                                     "ANTHROPIC_API_KEY": "a-key"}, clear=True):
            gen = QueryGenerator()
            self.assertFalse(gen.is_available())

    def test_placeholder_key_is_unconfigured(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "your_api_key_here"},
                        clear=True):
            gen = QueryGenerator()
            self.assertFalse(gen.is_available())

    def test_anthropic_model_override(self):
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "a-key",
                                     "ANTHROPIC_MODEL": "claude-custom"}, clear=True):
            gen = QueryGenerator()
            self.assertEqual(gen.model, "claude-custom")


class TestAnthropicBackend(unittest.TestCase):
    """The Anthropic backend, with the SDK mocked in sys.modules."""

    def _fake_anthropic(self, response_text):
        fake_module = MagicMock()
        fake_client = MagicMock()
        fake_module.Anthropic.return_value = fake_client

        block = MagicMock()
        block.type = "text"
        block.text = response_text
        response = MagicMock()
        response.content = [block]
        fake_client.messages.create.return_value = response
        return fake_module, fake_client

    def test_generate_with_mocked_sdk(self):
        payload = ('[{"id": "beat_001", "youtube_query": "forest drone footage", '
                   '"stock_query": "forest"}]')
        fake_module, fake_client = self._fake_anthropic(payload)

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "a-key"}, clear=True), \
                patch.dict(sys.modules, {"anthropic": fake_module}):
            gen = QueryGenerator()
            result = gen.generate(
                [{"id": "beat_001", "text": "We walk through the woods."}], "Nature doc"
            )

        self.assertEqual(result["beat_001"]["youtube_query"], "forest drone footage")
        fake_client.messages.create.assert_called_once()
        kwargs = fake_client.messages.create.call_args.kwargs
        # System prompt is sent as a cached content block (prompt caching).
        self.assertEqual(kwargs["system"][0]["cache_control"]["type"], "ephemeral")
        # User content carries the beat, not the system prompt.
        self.assertIn("beat_001", kwargs["messages"][0]["content"])

    def test_generate_falls_back_on_sdk_error(self):
        fake_module, fake_client = self._fake_anthropic("ignored")
        fake_client.messages.create.side_effect = Exception("boom")

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "a-key"}, clear=True), \
                patch.dict(sys.modules, {"anthropic": fake_module}):
            gen = QueryGenerator()
            self.assertIsNone(gen.generate([{"id": "beat_001", "text": "hi"}]))

    def test_generate_falls_back_when_sdk_missing(self):
        # Force `import anthropic` to fail even if it is installed.
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "a-key"}, clear=True), \
                patch.dict(sys.modules, {"anthropic": None}):
            gen = QueryGenerator()
            self.assertIsNone(gen.generate([{"id": "beat_001", "text": "hi"}]))


if __name__ == "__main__":
    unittest.main()
