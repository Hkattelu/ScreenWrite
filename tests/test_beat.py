import unittest
from screenwrite.core.beat import Beat
from screenwrite.config import WORDS_PER_SECOND

class TestBeat(unittest.TestCase):
    def test_initialization(self):
        """Test basic initialization and duration calculation."""
        text = "This is a test beat with enough words."
        word_count = len(text.split())
        expected_duration = word_count / WORDS_PER_SECOND

        # Ensure we have enough words for minimum duration
        # 8 words / 2.5 = 3.2s
        beat = Beat(
            id="beat_001",
            text=text,
            stock_keyword="testing",
            youtube_search_phrase="python testing"
        )

        self.assertEqual(beat.id, "beat_001")
        self.assertEqual(beat.text, text)
        self.assertEqual(beat.stock_keyword, "testing")
        self.assertEqual(beat.youtube_search_phrase, "python testing")
        self.assertAlmostEqual(beat.duration, expected_duration)
        self.assertEqual(beat.asset_paths, {})
        self.assertEqual(beat.visual_type, 'auto')
        self.assertIsNone(beat.visual_content)

    def test_duration_calculation_logic(self):
        """Test that duration is exactly word_count / WORDS_PER_SECOND."""
        # WORDS_PER_SECOND is 2.5
        # 10 words -> 4.0 seconds
        text = "one " * 10
        beat = Beat(
            id="beat_calc",
            text=text.strip(),
            stock_keyword="math",
            youtube_search_phrase="math tutorial"
        )
        self.assertEqual(beat.duration, 4.0)

    def test_validation_min_duration(self):
        """Test validation fails for duration < 3s."""
        # 7 words / 2.5 = 2.8s (< 3.0s)
        text = "one " * 7
        with self.assertRaises(AssertionError) as cm:
            Beat(
                id="beat_short",
                text=text.strip(),
                stock_keyword="short",
                youtube_search_phrase="short video"
            )
        self.assertIn("not in 3-10 second range", str(cm.exception))

    def test_validation_max_duration(self):
        """Test validation fails for duration > 10s."""
        # 26 words / 2.5 = 10.4s (> 10.0s)
        text = "one " * 26
        with self.assertRaises(AssertionError) as cm:
            Beat(
                id="beat_long",
                text=text.strip(),
                stock_keyword="long",
                youtube_search_phrase="long video"
            )
        self.assertIn("not in 3-10 second range", str(cm.exception))

    def test_validation_empty_text(self):
        """Test validation fails for empty text."""
        with self.assertRaises(AssertionError) as cm:
            Beat(
                id="beat_empty",
                text="   ",
                stock_keyword="empty",
                youtube_search_phrase="empty video"
            )
        self.assertIn("Text cannot be empty", str(cm.exception))

    def test_valid_boundary_duration(self):
        """Test boundary conditions for duration."""
        # Minimum valid: 8 words / 2.5 = 3.2s
        text_min = "one " * 8
        beat_min = Beat(
            id="beat_min",
            text=text_min.strip(),
            stock_keyword="min",
            youtube_search_phrase="min video"
        )
        self.assertEqual(beat_min.duration, 3.2)

        # Maximum valid: 25 words / 2.5 = 10.0s
        text_max = "one " * 25
        beat_max = Beat(
            id="beat_max",
            text=text_max.strip(),
            stock_keyword="max",
            youtube_search_phrase="max video"
        )
        self.assertEqual(beat_max.duration, 10.0)

    def test_str_repr(self):
        """Test string representations."""
        text = "This is a relatively long text that should be truncated in the string representation because it exceeds the limit."
        beat = Beat(
            id="beat_repr",
            text=text,
            stock_keyword="repr",
            youtube_search_phrase="repr video"
        )

        # Check __str__
        str_rep = str(beat)
        self.assertIn("[beat_repr]", str_rep)
        self.assertTrue(str_rep.endswith("..."))

        # Check __repr__
        repr_rep = repr(beat)
        self.assertIn("Beat(id='beat_repr'", repr_rep)
        self.assertIn("words=", repr_rep)
        self.assertIn("type='auto'", repr_rep)

if __name__ == '__main__':
    unittest.main()
