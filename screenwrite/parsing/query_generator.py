"""
LLM-backed B-roll query generation.

Converts narration beats into *visual* B-roll search queries using the Gemini
REST API. The goal is footage where something is visibly happening on screen
(establishing shots, action, processes, scenery, archival) rather than a person
talking to camera.

The narration describes ideas; searching YouTube for the spoken words returns
explainer / talking-head videos. This module instead asks an LLM to describe
what should be *shown* on screen, producing far more relevant background B-roll.

It degrades gracefully: when no ``GEMINI_API_KEY`` is configured, or the API
call fails for any reason, ``generate`` returns ``None`` and the caller falls
back to the parser's heuristic queries.
"""

import json
import logging
import os
import re
from typing import Dict, List, Optional

import requests

from ..config import DEFAULT_GEMINI_MODEL, GEMINI_REQUEST_TIMEOUT

logger = logging.getLogger(__name__)

_GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)

# The "prompt" that turns narration into visual B-roll queries. This is the main
# lever for relevance: it forces the model to describe what is shown, not said,
# and to steer away from talking-head footage.
_SYSTEM_PROMPT = """You are a senior video editor choosing background footage \
for a voiceover-driven video. You will be given the video's context and a list \
of narration beats (the words spoken aloud). For EACH beat, write a search \
query describing a concrete VISUAL SCENE to show on screen while that line is \
spoken.

Good footage to aim for (any of these):
- Establishing shots, scenery, action, and processes filmed in the real world.
- Screen recordings and software/website/app UI captures (great for anything \
about apps, websites, browsing, or on-screen actions).
- Archival or historical footage from the relevant era.
- People performing an activity (dialing a phone, a tutor helping a student, \
hands typing on a keyboard) - this is fine and often ideal.

Rules - follow these carefully:
- Describe what should be SHOWN, not what is SAID. Do not echo the narration's \
wording.
- Write a plain, literal description of the scene. Do NOT add production \
labels like "b-roll", "footage", "stock", "no commentary", or "royalty free" - \
those words pull up low-quality generic clip packs and hurt relevance.
- Beware figurative or ambiguous words that collide with game/movie/product \
titles. Translate the MEANING into a literal scene instead of searching the \
word. (e.g. an industry that "crashed" is not the game Crash - show an empty, \
dark 1980s arcade; a market "bubble" is not soap - show a frantic trading floor.)
- Prefer a generic, widely-available scene over a hyper-specific one, UNLESS \
the narration names a specific game/product/place you genuinely want footage \
OF (then keep that name, e.g. show actual NES gameplay).
- Avoid anyone speaking directly to camera: no interviews, podcasts, vlogs, \
reactions, lectures, news anchors, or explainer/talking-head videos. (People \
doing an activity are fine - just not someone addressing the camera.)
- Keep queries short (3-7 words). No beat numbers, no quotes, no narration.

For each beat return:
- "youtube_query": the literal scene description for YouTube. Keep a specific \
game/product/era name only when you want footage of that exact thing.
- "stock_query": a simpler 2-4 word GENERIC visual subject for a stock library \
(e.g. Pexels). Drop brand/proper names here (stock libraries won't have them); \
use the generic equivalent. Just the subject, no labels.

Examples:
Narration: "In 1983 the video game industry crashed and arcades went dark."
-> {"youtube_query": "empty dark 1980s arcade at night", "stock_query": \
"empty arcade"}
Narration: "When Nintendo revived gaming with the NES, we moved into the living \
room."
-> {"youtube_query": "1980s family playing nintendo in living room", \
"stock_query": "family watching television"}
Narration: "My favorite guides were text walkthroughs on sites like GameFAQs."
-> {"youtube_query": "scrolling an old website on a crt monitor", \
"stock_query": "person scrolling website"}
Narration: "In an age of forced ad-breaks, they feel like a breath of fresh air."
-> {"youtube_query": "calm sunrise over a quiet landscape", "stock_query": \
"peaceful sunrise"}

Return ONLY a JSON array, one object per beat, in the same order, shaped like:
[{"id": "beat_001", "youtube_query": "...", "stock_query": "..."}]
"""


def _load_api_key() -> Optional[str]:
    """Resolve the Gemini API key from the environment.

    The key is read from ``GEMINI_API_KEY``. Loading a project ``.env`` is the
    responsibility of the entry point (the CLI and web backend call
    ``load_dotenv``); keeping this function side-effect free ensures callers that
    have not configured a key - including unit tests - never trigger live API
    calls just by constructing a parser.
    """
    key = os.getenv("GEMINI_API_KEY")
    return key.strip() if key else None


class QueryGenerator:
    """Generates visual B-roll search queries for beats using the Gemini API."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the query generator.

        Args:
            api_key: Gemini API key. If None, read from GEMINI_API_KEY (or .env).
            model: Gemini model name. If None, read from GEMINI_MODEL env var or
                fall back to the configured default.
        """
        self.api_key = api_key or _load_api_key()
        # Treat the example placeholder as "not configured".
        if self.api_key in ("", "your_api_key_here"):
            self.api_key = None
        self.model = model or os.getenv("GEMINI_MODEL") or DEFAULT_GEMINI_MODEL

        if self.api_key:
            logger.info("Gemini query generation enabled (model: %s)", self.model)
        else:
            logger.debug(
                "No GEMINI_API_KEY configured; using heuristic B-roll queries"
            )

    def is_available(self) -> bool:
        """Return True if an API key is configured and generation can be attempted."""
        return bool(self.api_key)

    def generate(
        self, beats: List[Dict[str, str]], context: str = ""
    ) -> Optional[Dict[str, Dict[str, str]]]:
        """
        Generate visual B-roll queries for a batch of beats.

        Args:
            beats: List of {'id': ..., 'text': ...} dicts (the narration beats).
            context: Video-level context (title, section headers) to inform the
                visual choices.

        Returns:
            Mapping of beat id -> {'youtube_query': ..., 'stock_query': ...}, or
            None if generation is unavailable or fails (caller should fall back).
        """
        if not self.is_available():
            return None

        if not beats:
            return {}

        prompt = self._build_prompt(beats, context)

        try:
            raw = self._call_gemini(prompt)
        except Exception as e:  # noqa: BLE001 - any failure must fall back cleanly
            logger.warning("Gemini query generation failed, falling back: %s", e)
            return None

        parsed = self._parse_response(raw)
        if parsed is None:
            logger.warning("Could not parse Gemini response; falling back")
            return None

        return parsed

    def _build_prompt(self, beats: List[Dict[str, str]], context: str) -> str:
        """Assemble the full prompt from the system instructions, context, and beats."""
        lines = [_SYSTEM_PROMPT, ""]
        if context.strip():
            lines.append(f"Video context: {context.strip()}")
            lines.append("")
        lines.append("Beats:")
        for beat in beats:
            beat_id = beat.get("id", "")
            text = (beat.get("text", "") or "").replace("\n", " ").strip()
            lines.append(f"{beat_id}: {text}")
        return "\n".join(lines)

    def _call_gemini(self, prompt: str) -> str:
        """Call the Gemini generateContent endpoint and return the raw text part."""
        url = _GEMINI_ENDPOINT.format(model=self.model)
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.4,
                "responseMimeType": "application/json",
            },
        }

        response = requests.post(
            url,
            params={"key": self.api_key},
            json=payload,
            timeout=GEMINI_REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()

        candidates = data.get("candidates") or []
        if not candidates:
            raise ValueError("Gemini response contained no candidates")

        parts = candidates[0].get("content", {}).get("parts") or []
        if not parts:
            raise ValueError("Gemini response contained no content parts")

        return parts[0].get("text", "")

    def _parse_response(
        self, raw: str
    ) -> Optional[Dict[str, Dict[str, str]]]:
        """Parse the model's JSON array into a beat-id -> queries mapping."""
        if not raw or not raw.strip():
            return None

        text = raw.strip()
        # Strip Markdown code fences if the model added them despite the JSON mime.
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

        try:
            items = json.loads(text)
        except json.JSONDecodeError:
            # Last resort: extract the first JSON array in the text.
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if not match:
                return None
            try:
                items = json.loads(match.group(0))
            except json.JSONDecodeError:
                return None

        if not isinstance(items, list):
            return None

        result: Dict[str, Dict[str, str]] = {}
        for item in items:
            if not isinstance(item, dict):
                continue
            beat_id = item.get("id")
            if not beat_id:
                continue
            youtube_query = (item.get("youtube_query") or "").strip()
            stock_query = (item.get("stock_query") or "").strip()
            if not youtube_query and not stock_query:
                continue
            result[beat_id] = {
                "youtube_query": youtube_query,
                "stock_query": stock_query,
            }

        return result or None
