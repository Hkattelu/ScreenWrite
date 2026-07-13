"""
Local voiceover transcription with word-level timestamps.

Wraps faster-whisper behind one function so the rest of the VO-conform stage
only sees plain WordStamp values and never imports the heavy dependency.
faster-whisper is an optional extra (``pip install 'screenwrite[vo]'``) and is
imported lazily - constructing parsers/orchestrators without --vo must work on
machines that don't have it installed.
"""

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

from ..config import VO_WHISPER_MODEL, VO_WHISPER_DEVICE, VO_WHISPER_COMPUTE
from ..utils.error_handling import DependencyError

logger = logging.getLogger(__name__)


@dataclass
class WordStamp:
    """One transcribed word with its time range in the audio (seconds)."""
    word: str
    start: float
    end: float


def _default_download_root() -> str:
    """Whisper model cache, colocated with the tool's other caches."""
    root = Path.home() / ".cache" / "screenwrite" / "whisper"
    root.mkdir(parents=True, exist_ok=True)
    return str(root)


def transcribe_words(
    audio_path: str,
    model_size: Optional[str] = None,
    device: str = VO_WHISPER_DEVICE,
    compute_type: str = VO_WHISPER_COMPUTE,
    download_root: Optional[str] = None,
) -> Tuple[List[WordStamp], float]:
    """
    Transcribe a VO audio file into word timestamps.

    Args:
        audio_path: Path to the voiceover audio (wav/mp3/m4a/... - anything
            ffmpeg can decode).
        model_size: faster-whisper model name (default from config; the CLI's
            --whisper-model overrides).
        device: Inference device ("cpu" default - fast enough for VO length).
        compute_type: Quantization ("int8" keeps CPU inference light).
        download_root: Model cache directory (default ~/.cache/screenwrite/whisper).

    Returns:
        (words, audio_duration_seconds). Words are in audio order.

    Raises:
        DependencyError: If faster-whisper is not installed.
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError as e:
        raise DependencyError(
            "faster-whisper is required for --vo conform but is not installed. "
            "Install it with: pip install 'screenwrite[vo]' (or pip install faster-whisper)"
        ) from e

    model_size = model_size or VO_WHISPER_MODEL
    logger.info("Transcribing VO with faster-whisper (model=%s, device=%s)", model_size, device)

    model = WhisperModel(
        model_size,
        device=device,
        compute_type=compute_type,
        download_root=download_root or _default_download_root(),
    )

    # vad_filter skips long silences (whisper hallucinates words there);
    # condition_on_previous_text=False prevents repetition loops on retakes.
    segments, info = model.transcribe(
        audio_path,
        word_timestamps=True,
        vad_filter=True,
        condition_on_previous_text=False,
    )

    words: List[WordStamp] = []
    for segment in segments:
        for word in (segment.words or []):
            words.append(WordStamp(word=word.word, start=float(word.start), end=float(word.end)))

    duration = float(info.duration or (words[-1].end if words else 0.0))
    logger.info("Transcribed %d words over %.1fs of audio", len(words), duration)
    return words, duration
