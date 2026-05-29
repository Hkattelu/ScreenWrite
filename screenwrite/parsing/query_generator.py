"""
LLM-backed B-roll query generation.

Converts narration beats into *visual* B-roll search queries using an LLM. The
goal is footage where something is visibly happening on screen (establishing
shots, action, processes, scenery, archival) rather than a person talking to
camera.

The narration describes ideas; searching YouTube for the spoken words returns
explainer / talking-head videos. This module instead asks an LLM to describe
what should be *shown* on screen, producing far more relevant background B-roll.

Two backends are supported and selected automatically:

- **Anthropic (Claude)** when ``ANTHROPIC_API_KEY`` is set.
- **Gemini** when ``GEMINI_API_KEY`` is set.

The provider can be pinned with ``BROLL_LLM_PROVIDER`` (``auto`` | ``anthropic``
| ``gemini`` | ``none``); ``auto`` (the default) prefers Anthropic, then Gemini.

It degrades gracefully: when no key is configured, the chosen provider's SDK is
missing, or an API call fails for any reason, ``generate`` returns ``None`` and
the caller falls back to the parser's heuristic queries.
"""

import json
import logging
import os
import re
from typing import Dict, List, Optional, Tuple

import requests

from ..config import (
    DEFAULT_GEMINI_MODEL,
    GEMINI_REQUEST_TIMEOUT,
    DEFAULT_ANTHROPIC_MODEL,
    ANTHROPIC_REQUEST_TIMEOUT,
    ANTHROPIC_MAX_TOKENS,
)

logger = logging.getLogger(__name__)

_GEMINI_ENDPOINT = (
    "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
)

# Placeholder values that mean "not actually configured".
_PLACEHOLDER_KEYS = {"", "your_api_key_here"}

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


def _clean_key(key: Optional[str]) -> Optional[str]:
    """Return a stripped key, or None if it is missing/placeholder."""
    if not key:
        return None
    key = key.strip()
    return None if key in _PLACEHOLDER_KEYS else key


class QueryGenerator:
    """Generates visual B-roll search queries for beats using an LLM backend."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
    ):
        """
        Initialize the query generator.

        Args:
            api_key: Explicit API key. When given, it is used directly and the
                provider defaults to Gemini unless ``provider`` says otherwise
                (preserving the historical single-provider behavior). If None,
                a key is resolved from the environment per the selected provider.
            model: Model name override. If None, resolved from the provider's
                ``*_MODEL`` env var or the configured default.
            provider: ``auto`` (default) | ``anthropic`` | ``gemini`` | ``none``.
                If None, read from ``BROLL_LLM_PROVIDER`` (default ``auto``).
        """
        self.provider, self.api_key, self.model = self._resolve(
            api_key, model, provider
        )

        if self.api_key:
            logger.info(
                "LLM query generation enabled (provider: %s, model: %s)",
                self.provider, self.model,
            )
        else:
            logger.debug(
                "No LLM key configured (provider: %s); using heuristic B-roll "
                "queries", self.provider,
            )

    @staticmethod
    def _resolve(
        api_key: Optional[str],
        model: Optional[str],
        provider: Optional[str],
    ) -> Tuple[str, Optional[str], Optional[str]]:
        """Resolve (provider, api_key, model) from args and the environment.

        Returns a provider name even when no key is available, so callers can
        log a useful reason; ``is_available`` keys off the resolved api_key.
        """
        requested = (provider or os.getenv("BROLL_LLM_PROVIDER") or "auto").strip().lower()

        if requested == "none":
            return "none", None, None

        # When an api_key argument is supplied at all (even a placeholder), it is
        # authoritative: we do NOT fall back to environment keys. It uses Gemini
        # by default (historical behavior) unless the caller pinned a provider.
        # A placeholder cleans to None -> resolves as unconfigured.
        if api_key is not None:
            chosen = requested if requested in ("anthropic", "gemini") else "gemini"
            return chosen, _clean_key(api_key), QueryGenerator._resolve_model(chosen, model)

        anthropic_key = _clean_key(os.getenv("ANTHROPIC_API_KEY"))
        gemini_key = _clean_key(os.getenv("GEMINI_API_KEY"))

        if requested == "anthropic":
            return "anthropic", anthropic_key, QueryGenerator._resolve_model("anthropic", model)
        if requested == "gemini":
            return "gemini", gemini_key, QueryGenerator._resolve_model("gemini", model)

        # auto: prefer Anthropic, then Gemini.
        if anthropic_key:
            return "anthropic", anthropic_key, QueryGenerator._resolve_model("anthropic", model)
        if gemini_key:
            return "gemini", gemini_key, QueryGenerator._resolve_model("gemini", model)

        # Nothing configured. Report 'auto' so the debug log is accurate.
        return "auto", None, None

    @staticmethod
    def _resolve_model(provider: str, model: Optional[str]) -> str:
        """Pick the model for a provider from an override, env var, or default."""
        if model:
            return model
        if provider == "anthropic":
            return os.getenv("ANTHROPIC_MODEL") or DEFAULT_ANTHROPIC_MODEL
        return os.getenv("GEMINI_MODEL") or DEFAULT_GEMINI_MODEL

    def is_available(self) -> bool:
        """Return True if a key is configured and generation can be attempted."""
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

        user_content = self._build_user_content(beats, context)

        try:
            raw = self._call_backend(user_content)
        except Exception as e:  # noqa: BLE001 - any failure must fall back cleanly
            logger.warning("LLM query generation failed, falling back: %s", e)
            return None

        parsed = self._parse_response(raw)
        if parsed is None:
            logger.warning("Could not parse LLM response; falling back")
            return None

        return parsed

    def _call_backend(self, user_content: str) -> str:
        """Dispatch to the configured provider's backend."""
        if self.provider == "anthropic":
            return self._call_anthropic(user_content)
        return self._call_gemini(user_content)

    def _build_user_content(self, beats: List[Dict[str, str]], context: str) -> str:
        """Assemble the per-request content (context + beats), without the system prompt."""
        lines: List[str] = []
        if context.strip():
            lines.append(f"Video context: {context.strip()}")
            lines.append("")
        lines.append("Beats:")
        for beat in beats:
            beat_id = beat.get("id", "")
            text = (beat.get("text", "") or "").replace("\n", " ").strip()
            lines.append(f"{beat_id}: {text}")
        return "\n".join(lines)

    def _call_gemini(self, user_content: str) -> str:
        """Call the Gemini generateContent endpoint and return the raw text part."""
        # Gemini takes a single combined prompt (system instructions + content).
        prompt = f"{_SYSTEM_PROMPT}\n\n{user_content}"
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

    def _call_anthropic(self, user_content: str) -> str:
        """Call the Anthropic Messages API and return the raw text content.

        The static system prompt is sent as a cached content block so repeated
        batches in the same run reuse it cheaply (prompt caching).
        """
        try:
            import anthropic  # Lazy import: optional dependency.
        except ImportError as e:
            raise RuntimeError(
                "anthropic package not installed; run 'pip install anthropic' or "
                "set BROLL_LLM_PROVIDER=gemini"
            ) from e

        client = anthropic.Anthropic(api_key=self.api_key)
        response = client.messages.create(
            model=self.model,
            max_tokens=ANTHROPIC_MAX_TOKENS,
            system=[
                {
                    "type": "text",
                    "text": _SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": user_content}],
            timeout=ANTHROPIC_REQUEST_TIMEOUT,
        )

        texts = [
            block.text
            for block in (response.content or [])
            if getattr(block, "type", None) == "text"
        ]
        if not texts:
            raise ValueError("Anthropic response contained no text content")
        return "".join(texts)

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
