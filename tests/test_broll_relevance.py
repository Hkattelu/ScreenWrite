"""
Tests for B-roll relevance improvements:
- LLM (Gemini) visual query generation (QueryGenerator)
- YouTube result filtering/ranking away from talking-head footage
- Specificity-based fetcher ordering in the AssetOrchestrator

All tests are offline: the Gemini HTTP call is mocked and no real downloads or
searches are performed.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from screenwrite.parsing.query_generator import QueryGenerator
from screenwrite.fetchers.youtube_client import YouTubeClient
from screenwrite.fetchers.asset_orchestrator import AssetOrchestrator


class TestQueryGenerator(unittest.TestCase):
    """Visual B-roll query generation via the Gemini API."""

    def test_unavailable_without_key(self):
        with patch.dict(os.environ, {}, clear=True):
            gen = QueryGenerator()
            self.assertFalse(gen.is_available())

    def test_placeholder_key_treated_as_unconfigured(self):
        gen = QueryGenerator(api_key="your_api_key_here")
        self.assertFalse(gen.is_available())

    def test_available_with_key(self):
        gen = QueryGenerator(api_key="real-key")
        self.assertTrue(gen.is_available())

    def test_generate_returns_none_when_unavailable(self):
        with patch.dict(os.environ, {}, clear=True):
            gen = QueryGenerator()
            # Must not attempt any network call when no key is configured.
            self.assertIsNone(gen.generate([{"id": "beat_001", "text": "hi"}]))

    def test_parse_clean_json(self):
        gen = QueryGenerator(api_key="real-key")
        raw = ('[{"id": "beat_001", "youtube_query": "aerial city footage", '
               '"stock_query": "city skyline"}]')
        parsed = gen._parse_response(raw)
        self.assertEqual(parsed["beat_001"]["youtube_query"], "aerial city footage")
        self.assertEqual(parsed["beat_001"]["stock_query"], "city skyline")

    def test_parse_strips_code_fences(self):
        gen = QueryGenerator(api_key="real-key")
        raw = '```json\n[{"id": "beat_001", "youtube_query": "rain on window"}]\n```'
        parsed = gen._parse_response(raw)
        self.assertEqual(parsed["beat_001"]["youtube_query"], "rain on window")

    def test_parse_garbage_returns_none(self):
        gen = QueryGenerator(api_key="real-key")
        self.assertIsNone(gen._parse_response("not json at all"))
        self.assertIsNone(gen._parse_response(""))

    def test_generate_with_mocked_api(self):
        gen = QueryGenerator(api_key="real-key")
        payload_text = ('[{"id": "beat_001", "youtube_query": "forest drone footage", '
                        '"stock_query": "forest"}]')
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "candidates": [{"content": {"parts": [{"text": payload_text}]}}]
        }
        with patch("screenwrite.parsing.query_generator.requests") as mock_requests:
            mock_requests.post.return_value = mock_response
            result = gen.generate([{"id": "beat_001", "text": "We walk through the woods."}], "Nature doc")

        self.assertIn("beat_001", result)
        self.assertEqual(result["beat_001"]["youtube_query"], "forest drone footage")
        # The query should have actually been sent to the Gemini endpoint.
        mock_requests.post.assert_called_once()

    def test_generate_falls_back_on_http_error(self):
        gen = QueryGenerator(api_key="real-key")
        with patch("screenwrite.parsing.query_generator.requests") as mock_requests:
            mock_requests.post.side_effect = Exception("boom")
            self.assertIsNone(gen.generate([{"id": "beat_001", "text": "hi"}]))


class TestYouTubeRanking(unittest.TestCase):
    """Filtering/ranking of YouTube candidates toward background B-roll."""

    def setUp(self):
        self.client = YouTubeClient()

    def test_talking_head_titles_are_penalized(self):
        broll = {"title": "City Skyline Cinematic B-Roll Footage 4K", "duration": 60}
        talking = {"title": "Tech CEO Interview - Full Podcast Episode", "duration": 60}
        self.assertGreater(
            self.client._score_entry(broll), self.client._score_entry(talking)
        )
        self.assertLess(self.client._score_entry(talking), 0)

    def test_duration_bounds(self):
        self.assertTrue(self.client._duration_ok({"duration": 60}))
        self.assertFalse(self.client._duration_ok({"duration": 5}))      # too short
        self.assertFalse(self.client._duration_ok({"duration": 99999}))  # too long
        self.assertTrue(self.client._duration_ok({"duration": 0}))       # unknown allowed
        self.assertTrue(self.client._duration_ok({}))                    # missing allowed

    def test_rank_demotes_talking_heads(self):
        entries = [
            {"title": "Founder Interview Podcast", "duration": 600, "url": "a"},
            {"title": "Aerial Drone Footage of Mountains 4K", "duration": 60, "url": "b"},
            {"title": "News Conference Highlights", "duration": 120, "url": "c"},
        ]
        ranked = self.client._rank_and_filter(entries, count=3)
        # Best B-roll should be first.
        self.assertEqual(ranked[0]["url"], "b")

    def test_rank_respects_count_and_never_empty(self):
        entries = [{"title": "Some Interview", "duration": 30, "url": str(i)} for i in range(10)]
        ranked = self.client._rank_and_filter(entries, count=3)
        self.assertEqual(len(ranked), 3)
        # Even when all candidates are out of duration range, return something.
        bad = [{"title": "x", "duration": 1, "url": "z"}]
        self.assertEqual(len(self.client._rank_and_filter(bad, count=3)), 1)

    def test_query_terms_boost_on_topic_titles(self):
        # Both are equally "good" B-roll (aerial drone), but only one is on-topic.
        on_topic = {"title": "Aerial Drone Mountain Range", "duration": 60, "url": "a"}
        off_topic = {"title": "Aerial Drone Beach Sunset", "duration": 60, "url": "b"}
        ranked = self.client._rank_and_filter(
            [off_topic, on_topic], count=2, query="snowy mountain peaks"
        )
        self.assertEqual(ranked[0]["url"], "a")

    def test_score_entry_single_arg_still_works(self):
        # Backward-compatible signature: query terms are optional.
        score = self.client._score_entry({"title": "Cinematic Aerial 4K"})
        self.assertGreater(score, 0)

    def test_pick_start_offset(self):
        # Unknown/short sources -> no offset (safe).
        self.assertEqual(self.client._pick_start_offset(None, 5.0), 0.0)
        self.assertEqual(self.client._pick_start_offset(0, 5.0), 0.0)
        self.assertEqual(self.client._pick_start_offset(7.0, 5.0), 0.0)  # no room
        # Long source -> skips an intro and keeps the full segment in bounds.
        offset = self.client._pick_start_offset(120.0, 5.0)
        self.assertGreater(offset, 0.0)
        self.assertLessEqual(offset + 5.0, 120.0)


class TestFetcherOrdering(unittest.TestCase):
    """Specificity-based ordering of fetchers in the AssetOrchestrator."""

    def setUp(self):
        # Both fetchers initialize without keys/network; Pexels just warns.
        self.orch = AssetOrchestrator(youtube_enabled=True, pexels_enabled=True)

    def test_specific_query_detection(self):
        self.assertTrue(self.orch._is_specific_query("World War footage"))      # proper noun
        self.assertTrue(self.orch._is_specific_query("the moon landing 1969"))  # year
        self.assertTrue(self.orch._is_specific_query('a clip of "Hey Jude"'))   # quoted
        self.assertFalse(self.orch._is_specific_query("people walking in a city"))
        self.assertFalse(self.orch._is_specific_query(""))

    def test_generic_query_prefers_stock_first(self):
        order = [f.name for f in self.orch._order_fetchers("people walking outside")]
        # Pexels (stock) should lead for a generic query.
        self.assertEqual(order[0], "Pexels")

    def test_specific_query_keeps_youtube_first(self):
        order = [f.name for f in self.orch._order_fetchers("Apollo 11 launch 1969")]
        self.assertEqual(order[0], "YouTube")

    def test_flag_off_keeps_default_order(self):
        orch = AssetOrchestrator(
            youtube_enabled=True, pexels_enabled=True, prefer_stock_for_generic=False
        )
        order = [f.name for f in orch._order_fetchers("people walking outside")]
        self.assertEqual(order[0], "YouTube")


if __name__ == "__main__":
    unittest.main()
