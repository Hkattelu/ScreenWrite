"""VO-first conform: cut the timeline to the recorded voiceover, not to word-count guesses."""

import logging
from typing import List, Optional

from .transcriber import WordStamp, transcribe_words
from .aligner import BeatSpan, VOConformReport, conform, tokenize

from ..config import DEFAULT_FRAMERATE

logger = logging.getLogger(__name__)

__all__ = [
    'WordStamp', 'BeatSpan', 'VOConformReport',
    'transcribe_words', 'conform', 'tokenize', 'conform_beats_to_vo',
]


def conform_beats_to_vo(
    vo_path: str,
    beats: List,
    model_size: Optional[str] = None,
    framerate: int = DEFAULT_FRAMERATE,
) -> VOConformReport:
    """
    Transcribe a VO recording and conform beats to its real timing.

    Mutates each beat in place: ``duration`` becomes the boundary-to-boundary
    time (frame-quantized, so cumulative sums are exact), and ``vo_start`` /
    ``vo_end`` / ``vo_matched`` carry the absolute positions for downstream
    consumers (Resolve builder, coverage reports).

    Args:
        vo_path: Path to the voiceover audio file.
        beats: Parsed Beat objects, in script order.
        model_size: faster-whisper model override (default from config).
        framerate: Timeline framerate for quantization.

    Returns:
        The VOConformReport (also useful for pacing preview in --dry-run).
    """
    words, audio_duration = transcribe_words(vo_path, model_size=model_size)
    report = conform(
        [beat.text for beat in beats], words, audio_duration, framerate=framerate
    )

    logger.info("VO pacing (beat | est -> vo start-end | dur | text coverage):")
    for beat, timing in zip(beats, report.beat_timings()):
        logger.info(
            "  %s | %5.1fs -> %6.1f-%6.1fs | %5.1fs | %3.0f%%%s",
            beat.id, beat.duration, timing['start'], timing['end'],
            timing['duration'], timing['coverage'] * 100,
            '' if timing['matched'] else '  (NOT FOUND IN VO)',
        )
        beat.duration = timing['duration']
        beat.vo_start = timing['start']
        beat.vo_end = timing['end']
        beat.vo_matched = timing['matched']

    matched = sum(1 for s in report.spans if s.matched)
    logger.info(
        "Conformed %d/%d beats to VO (%.1fs audio, %.0f%% script coverage)",
        matched, len(beats), audio_duration, report.overall_coverage * 100,
    )
    return report
