"""
Tests for VO-first conform: script-to-voiceover alignment, cut placement,
frame quantization, and timeline integration.

No faster-whisper needed - WordStamp lists are fabricated directly.
"""

import unittest
import xml.etree.ElementTree as ET
import tempfile
from pathlib import Path

from screenwrite.core.beat import Beat
from screenwrite.generators.xml_generator import XMLGenerator
from screenwrite.utils.error_handling import InputValidationError
from screenwrite.vo.aligner import (
    align_beat_spans,
    compute_boundaries,
    conform,
    tokenize,
)
from screenwrite.vo.transcriber import WordStamp

FPS = 30


def read_words(text: str, start: float, words_per_second: float = 2.5):
    """Fabricate WordStamps for a text read at a steady rate from `start`."""
    stamps = []
    t = start
    step = 1.0 / words_per_second
    for token in text.split():
        stamps.append(WordStamp(word=f" {token}", start=t, end=t + step * 0.8))
        t += step
    return stamps


BEAT1 = "The Bell Gargoyles are where the difficulty really bares its teeth for players"
BEAT2 = "Blighttown is the perfect example of an area that everyone hates deeply"
BEAT3 = "And the duo fight in Anor Londo asks you to prove you learned something"


class TestTokenize(unittest.TestCase):
    def test_normalizes_case_and_punctuation(self):
        self.assertEqual(tokenize(" Hello, World! it's 2-day "),
                         ['hello', 'world', "it's", '2', 'day'])

    def test_empty(self):
        self.assertEqual(tokenize(''), [])
        self.assertEqual(tokenize(None), [])


class TestAlignment(unittest.TestCase):
    def test_perfect_read_all_matched_and_contiguous(self):
        words = read_words(BEAT1, 0.5) + read_words(BEAT2, 7.0) + read_words(BEAT3, 13.0)
        spans = align_beat_spans([tokenize(BEAT1), tokenize(BEAT2), tokenize(BEAT3)], words)
        self.assertTrue(all(s.matched for s in spans))
        self.assertTrue(all(s.coverage == 1.0 for s in spans))
        # Monotonic, non-overlapping
        self.assertLess(spans[0].end, spans[1].start)
        self.assertLess(spans[1].end, spans[2].start)

    def test_reworded_line_still_matches_on_anchors(self):
        # ~50% of the words changed, nouns kept
        reworded = "so the Bell Gargoyles happen to be exactly where difficulty shows teeth"
        words = read_words(reworded, 1.0) + read_words(BEAT2, 8.0)
        spans = align_beat_spans([tokenize(BEAT1), tokenize(BEAT2)], words)
        self.assertTrue(spans[0].matched)
        self.assertLess(spans[0].coverage, 1.0)
        self.assertTrue(spans[1].matched)

    def test_skipped_paragraph_unmatched(self):
        words = read_words(BEAT1, 0.5) + read_words(BEAT3, 8.0)  # BEAT2 never read
        spans = align_beat_spans(
            [tokenize(BEAT1), tokenize(BEAT2), tokenize(BEAT3)], words)
        self.assertTrue(spans[0].matched)
        self.assertFalse(spans[1].matched)
        self.assertTrue(spans[2].matched)

    def test_retake_stays_monotonic(self):
        # BEAT2 read twice (retake); alignment must keep spans ordered
        words = (read_words(BEAT1, 0.5) + read_words(BEAT2, 7.0)
                 + read_words(BEAT2, 14.0) + read_words(BEAT3, 21.0))
        spans = align_beat_spans([tokenize(BEAT1), tokenize(BEAT2), tokenize(BEAT3)], words)
        self.assertTrue(all(s.matched for s in spans))
        self.assertLessEqual(spans[0].end, spans[1].start)
        self.assertLessEqual(spans[1].end, spans[2].start)


class TestBoundaries(unittest.TestCase):
    def _conform(self, texts, words, duration):
        return conform(texts, words, duration, framerate=FPS)

    def test_leading_silence_absorbed_by_first_beat(self):
        words = read_words(BEAT1, 2.5) + read_words(BEAT2, 9.0)
        report = self._conform([BEAT1, BEAT2], words, 15.0)
        self.assertEqual(report.boundaries_frames[0], 0)
        timings = report.beat_timings()
        self.assertEqual(timings[0]['start'], 0.0)

    def test_cut_at_pause_midpoint_frame_quantized(self):
        words = read_words(BEAT1, 0.0) + read_words(BEAT2, 10.0)
        report = self._conform([BEAT1, BEAT2], words, 16.0)
        span1_end = max(w.end for w in words[:len(BEAT1.split())])
        midpoint = (span1_end + 10.0) / 2
        self.assertEqual(report.boundaries_frames[1], round(midpoint * FPS))

    def test_trailing_audio_absorbed_by_last_beat(self):
        words = read_words(BEAT1, 0.0) + read_words(BEAT2, 7.0)
        report = self._conform([BEAT1, BEAT2], words, 30.0)
        self.assertEqual(report.boundaries_frames[-1], round(30.0 * FPS))
        self.assertEqual(report.beat_timings()[-1]['end'], 30.0)

    def test_skipped_beat_collapses_to_zero_with_warning(self):
        words = read_words(BEAT1, 0.0) + read_words(BEAT3, 9.0)
        report = self._conform([BEAT1, BEAT2, BEAT3], words, 16.0)
        timings = report.beat_timings()
        self.assertEqual(timings[1]['duration'], 0.0)
        self.assertFalse(timings[1]['matched'])
        self.assertTrue(any('beat_002' in w and 'not found' in w for w in report.warnings))
        # Neighbors share the collapsed boundary; totals still cover the audio
        self.assertEqual(timings[0]['end'], timings[1]['start'])
        self.assertEqual(timings[1]['end'], timings[2]['start'])
        self.assertEqual(timings[2]['end'], 16.0)

    def test_adlib_gap_warns(self):
        # 8s of unscripted speech between the two beats
        adlib = read_words("totally unrelated rambling about something else entirely here", 6.0)
        words = read_words(BEAT1, 0.0) + adlib + read_words(BEAT2, 14.0)
        report = self._conform([BEAT1, BEAT2], words, 22.0)
        self.assertTrue(any('unscripted VO' in w for w in report.warnings))

    def test_wrong_audio_raises(self):
        words = read_words("completely different narration about cooking pasta al dente", 0.0)
        with self.assertRaises(InputValidationError):
            self._conform([BEAT1, BEAT2], words, 10.0)

    def test_no_matched_beats_raises(self):
        with self.assertRaises(InputValidationError):
            compute_boundaries(
                align_beat_spans([tokenize(BEAT1)], []), 10.0)

    def test_durations_sum_exactly_to_audio(self):
        words = read_words(BEAT1, 1.2) + read_words(BEAT2, 8.7) + read_words(BEAT3, 15.3)
        report = self._conform([BEAT1, BEAT2, BEAT3], words, 21.37)
        total_frames = sum(
            round(t['duration'] * FPS) for t in report.beat_timings()
        )
        self.assertEqual(total_frames, round(21.37 * FPS))


class TestXMLIntegration(unittest.TestCase):
    def test_conformed_offsets_and_zero_duration_skip(self):
        texts = [BEAT1, BEAT2, BEAT3]
        beats = [
            Beat(id=f'beat_{i+1:03d}', text=t, stock_keyword='', youtube_search_phrase='')
            for i, t in enumerate(texts)
        ]
        # BEAT2 skipped in the VO
        words = read_words(BEAT1, 0.0) + read_words(BEAT3, 9.0)
        report = conform(texts, words, 16.0, framerate=FPS)
        for beat, timing in zip(beats, report.beat_timings()):
            beat.duration = timing['duration']
            beat.vo_start = timing['start']
            beat.vo_end = timing['end']
            beat.vo_matched = timing['matched']

        generator = XMLGenerator()
        with tempfile.TemporaryDirectory() as tmp:
            output = str(Path(tmp) / 'timeline.fcpxml')
            generator.generate(beats, {b.id: None for b in beats}, output)
            root = ET.parse(output).getroot()

        spine = root.find('.//spine')
        gaps = spine.findall('gap')
        # beat_002 (0 frames) emits nothing
        self.assertEqual(len(gaps), 2)
        names = [g.get('name') for g in gaps]
        self.assertNotIn('Gap - beat_002', names)
        # Offsets equal the quantized boundaries
        self.assertEqual(gaps[0].get('offset'), '0/30s')
        expected_offset = report.boundaries_frames[2]
        self.assertEqual(gaps[1].get('offset'), f'{expected_offset}/30s')
        # Second gap runs to the end of the audio
        self.assertEqual(
            int(gaps[1].get('duration').split('/')[0]),
            round(16.0 * FPS) - expected_offset,
        )


if __name__ == '__main__':
    unittest.main()
