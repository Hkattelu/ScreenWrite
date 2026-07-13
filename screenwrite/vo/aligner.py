"""
Script-to-voiceover alignment: beats -> real time ranges in the recorded VO.

Pure logic with no external dependencies (fully unit-testable without
faster-whisper). The transcript words and the concatenated script tokens are
aligned with difflib.SequenceMatcher, whose matching blocks are monotonic in
both sequences - so beat spans come out in order even when the read deviates
from the script (rewordings, ad-libs, skipped paragraphs).

Cut placement rules:
- Beat 1 starts at 0 (it absorbs leading silence - the VO sits at timeline 0).
- Cuts between beats land at the midpoint of the inter-beat pause.
- Beats whose text never appears in the VO collapse to zero duration and are
  loudly flagged (re-record or delete the paragraph) - never guessed.
- The last matched beat absorbs trailing audio.

Boundaries are frame-quantized exactly once; durations are boundary-to-
boundary differences, so cumulative sums equal absolute VO positions with no
rounding drift.
"""

import logging
import re
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import List, Optional

from ..config import (
    DEFAULT_FRAMERATE,
    VO_MIN_BEAT_COVERAGE,
    VO_MIN_OVERALL_COVERAGE,
    VO_ADLIB_GAP_WARN_SECONDS,
)
from ..utils.error_handling import InputValidationError
from .transcriber import WordStamp

logger = logging.getLogger(__name__)


@dataclass
class BeatSpan:
    """Where one beat's words landed in the VO audio."""
    beat_index: int
    start: Optional[float]  # first matched word's start (seconds), None if unmatched
    end: Optional[float]    # last matched word's end (seconds), None if unmatched
    coverage: float         # matched beat tokens / total beat tokens
    matched: bool


@dataclass
class VOConformReport:
    """Result of conforming beats to a VO recording."""
    audio_duration: float
    spans: List[BeatSpan]
    boundaries_frames: List[int]  # N+1 frame-quantized cut points
    framerate: int
    overall_coverage: float
    warnings: List[str] = field(default_factory=list)

    def beat_timings(self) -> List[dict]:
        """Per-beat start/end/duration in seconds, from the quantized boundaries."""
        timings = []
        for i, span in enumerate(self.spans):
            start = self.boundaries_frames[i] / self.framerate
            end = self.boundaries_frames[i + 1] / self.framerate
            timings.append({
                'start': start,
                'end': end,
                'duration': end - start,
                'matched': span.matched,
                'coverage': span.coverage,
            })
        return timings


def tokenize(text: str) -> List[str]:
    """Normalize text to comparable lowercase word tokens."""
    return re.findall(r"[a-z0-9']+", (text or '').lower())


def align_beat_spans(
    beats_tokens: List[List[str]],
    words: List[WordStamp],
    min_coverage: float = VO_MIN_BEAT_COVERAGE,
) -> List[BeatSpan]:
    """
    Align each beat's tokens to transcript words.

    Args:
        beats_tokens: tokenize()d text of each beat, in script order.
        words: Transcript words with timestamps, in audio order.
        min_coverage: Fraction of a beat's tokens that must match for the beat
            to count as found in the VO.

    Returns:
        One BeatSpan per beat (monotonic starts/ends across matched beats).
    """
    # Flatten script tokens, remembering each beat's [lo, hi) token span.
    script_tokens: List[str] = []
    beat_token_ranges = []
    for tokens in beats_tokens:
        lo = len(script_tokens)
        script_tokens.extend(tokens)
        beat_token_ranges.append((lo, len(script_tokens)))

    # Normalize transcript words; a whisper "word" may normalize to 0..n
    # tokens, so keep a map from normalized-token index -> source WordStamp.
    vo_tokens: List[str] = []
    vo_token_word: List[WordStamp] = []
    for word in words:
        for token in tokenize(word.word):
            vo_tokens.append(token)
            vo_token_word.append(word)

    # Monotonic anchor blocks between script and VO token streams.
    matcher = SequenceMatcher(None, script_tokens, vo_tokens, autojunk=False)
    matched_word_by_script_index: dict = {}
    for block in matcher.get_matching_blocks():
        for k in range(block.size):
            matched_word_by_script_index[block.a + k] = vo_token_word[block.b + k]

    spans: List[BeatSpan] = []
    for beat_index, (lo, hi) in enumerate(beat_token_ranges):
        matched_words = [
            matched_word_by_script_index[i]
            for i in range(lo, hi)
            if i in matched_word_by_script_index
        ]
        total = max(1, hi - lo)
        coverage = len(matched_words) / total
        if matched_words and coverage >= min_coverage:
            spans.append(BeatSpan(
                beat_index=beat_index,
                start=min(w.start for w in matched_words),
                end=max(w.end for w in matched_words),
                coverage=coverage,
                matched=True,
            ))
        else:
            spans.append(BeatSpan(
                beat_index=beat_index,
                start=None,
                end=None,
                coverage=coverage,
                matched=False,
            ))
    return spans


def compute_boundaries(spans: List[BeatSpan], audio_duration: float) -> List[float]:
    """
    Turn beat spans into N+1 cut points covering [0, audio_duration].

    Cuts land at the midpoint of the pause between adjacent matched beats.
    Unmatched beats collapse onto the boundary between their matched
    neighbors (zero duration). Leading unmatched beats collapse to 0;
    trailing ones to audio_duration.
    """
    n = len(spans)
    matched_indices = [i for i, s in enumerate(spans) if s.matched]
    if not matched_indices:
        raise InputValidationError(
            "No beat could be located in the VO audio - is this the right file?"
        )

    boundaries = [0.0] * (n + 1)
    boundaries[n] = audio_duration

    # Boundary between each adjacent pair of matched beats: pause midpoint.
    # Every boundary index between them (unmatched beats) shares that point.
    for prev, nxt in zip(matched_indices, matched_indices[1:]):
        midpoint = (spans[prev].end + spans[nxt].start) / 2
        for boundary_index in range(prev + 1, nxt + 1):
            boundaries[boundary_index] = midpoint

    # Leading unmatched beats collapse to 0 (beat 1's cut is always at 0 so
    # the first visible clip covers any leading silence).
    for boundary_index in range(1, matched_indices[0] + 1):
        boundaries[boundary_index] = 0.0

    # Trailing unmatched beats collapse to the end; the last matched beat
    # absorbs trailing audio.
    for boundary_index in range(matched_indices[-1] + 1, n):
        boundaries[boundary_index] = audio_duration

    # Defensive monotonic clamp (matcher monotonicity should guarantee this).
    for i in range(1, n + 1):
        boundaries[i] = min(max(boundaries[i], boundaries[i - 1]), audio_duration)

    return boundaries


def conform(
    beats_texts: List[str],
    words: List[WordStamp],
    audio_duration: float,
    framerate: int = DEFAULT_FRAMERATE,
) -> VOConformReport:
    """
    Align beats to the VO and produce frame-quantized cut points.

    Args:
        beats_texts: Each beat's narration text, in script order.
        words: Transcript WordStamps.
        audio_duration: Length of the VO audio in seconds.
        framerate: Timeline framerate for quantization.

    Returns:
        VOConformReport with boundaries, spans, coverage, and warnings.

    Raises:
        InputValidationError: If the VO doesn't plausibly match the script.
    """
    beats_tokens = [tokenize(text) for text in beats_texts]
    spans = align_beat_spans(beats_tokens, words)

    total_tokens = sum(len(t) for t in beats_tokens)
    matched_tokens = sum(
        len(beats_tokens[s.beat_index]) * s.coverage for s in spans
    )
    overall_coverage = matched_tokens / max(1, total_tokens)
    if overall_coverage < VO_MIN_OVERALL_COVERAGE:
        raise InputValidationError(
            f"VO does not match the script (only {overall_coverage:.0%} of the "
            f"script was found in the audio) - wrong audio file?"
        )

    warnings: List[str] = []
    for span in spans:
        if not span.matched:
            warnings.append(
                f"beat_{span.beat_index + 1:03d}: text not found in VO - 0s "
                f"allocated, clip skipped (re-record or delete the paragraph)"
            )

    # Flag long unscripted runs between matched beats (ad-lib / retake).
    matched_spans = [s for s in spans if s.matched]
    for prev, nxt in zip(matched_spans, matched_spans[1:]):
        gap = nxt.start - prev.end
        if gap > VO_ADLIB_GAP_WARN_SECONDS:
            warnings.append(
                f"~{gap:.0f}s of unscripted VO between "
                f"beat_{prev.beat_index + 1:03d} and beat_{nxt.beat_index + 1:03d} "
                f"(at {prev.end:.1f}s) - possible ad-lib or retake; check the cut"
            )

    boundaries = compute_boundaries(spans, audio_duration)
    boundaries_frames = [round(b * framerate) for b in boundaries]
    # Quantization must preserve monotonicity too.
    for i in range(1, len(boundaries_frames)):
        boundaries_frames[i] = max(boundaries_frames[i], boundaries_frames[i - 1])

    return VOConformReport(
        audio_duration=audio_duration,
        spans=spans,
        boundaries_frames=boundaries_frames,
        framerate=framerate,
        overall_coverage=overall_coverage,
        warnings=warnings,
    )
