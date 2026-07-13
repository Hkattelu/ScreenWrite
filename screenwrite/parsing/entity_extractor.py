"""
LLM entity extraction + beat classification for game-essay scripts.

Replaces keyword-on-narration query generation for game scripts: each beat is
classified and its named in-game entities extracted, so downstream fetchers
can match ENTITIES against human-labeled sources (chapter markers, wiki pages)
instead of searching raw narration text.

Classification (drives source routing):
- "game_entity": the beat names >= 1 concrete in-game thing -> chaptered
  gameplay cascade.
- "abstract":    a point/opinion with no game referent -> atmospheric stock or
  manual flag. Never game footage.
- "manual_fill": needs the creator (talking-head, title card, personal shot).

Uses the same Gemini REST pattern as query_generator and degrades the same
way: no key or any failure -> ``extract`` returns None and the caller falls
back to the legacy pipeline.
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

_SYSTEM_PROMPT = """You are indexing a video-essay script about the video game \
"{game}" so each narration beat can be matched to gameplay footage. For EACH \
beat, extract named in-game entities and classify the beat.

"entities": named, concrete things from {game} that the beat is actually \
about - bosses, enemies, areas/locations, characters/NPCs, items, or named \
mechanics. Rules:
- Use the official in-game name (the name a wiki page or a walkthrough \
chapter would use), even when the narration abbreviates or misspells it.
- Only name entities from {game} itself. Do not invent entities, and do NOT \
write search phrases or scene descriptions - names only.
- A beat mentioning an entity in passing while making a general point is \
still about that entity only if footage of it would fit the line. Otherwise \
leave it out.
- Order entities by how central they are to the beat. Empty list if none.

"beat_class": exactly one of:
- "game_entity": the beat names at least one concrete in-game thing \
(entities is non-empty).
- "abstract": a point, opinion, or analysis with no concrete game referent \
(e.g. "this is where the pacing falls apart"). Common in essays - do not \
force an entity onto these.
- "manual_fill": only the creator can supply the visual - direct address to \
the audience, channel/sponsor talk, title cards, or a specific personal shot.

Return ONLY a JSON array, one object per beat, in the same order, shaped like:
[{{"id": "beat_001", "beat_class": "game_entity", "entities": ["Bell Gargoyles"]}}]
"""


def _load_api_key() -> Optional[str]:
    """Resolve the Gemini API key from the environment (see query_generator)."""
    key = os.getenv("GEMINI_API_KEY")
    return key.strip() if key else None


VALID_BEAT_CLASSES = ("game_entity", "abstract", "manual_fill")


class EntityExtractor:
    """Extracts game entities and beat classes for beats using the Gemini API."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """
        Initialize the extractor.

        Args:
            api_key: Gemini API key. If None, read from GEMINI_API_KEY (or .env).
            model: Gemini model name. If None, read from GEMINI_MODEL env var or
                fall back to the configured default.
        """
        self.api_key = api_key or _load_api_key()
        if self.api_key in ("", "your_api_key_here"):
            self.api_key = None
        self.model = model or os.getenv("GEMINI_MODEL") or DEFAULT_GEMINI_MODEL

    def is_available(self) -> bool:
        """Return True if an API key is configured and extraction can be attempted."""
        return bool(self.api_key)

    def extract(
        self,
        beats: List[Dict[str, str]],
        game: str,
        known_entities: Optional[List[str]] = None,
    ) -> Optional[Dict[str, Dict]]:
        """
        Extract entities and beat classes for a batch of beats.

        Args:
            beats: List of {'id': ..., 'text': ...} dicts (narration beats).
            game: The game the script is about (constrains the closed set).
            known_entities: Optional per-game entity list to sharpen precision
                (e.g. scraped from a wiki). Not required - the model's own
                knowledge of popular games is the primary source.

        Returns:
            Mapping of beat id -> {'beat_class': str, 'entities': List[str]},
            or None if extraction is unavailable or fails (caller falls back).
        """
        if not self.is_available():
            return None
        if not beats:
            return {}

        prompt = self._build_prompt(beats, game, known_entities)

        try:
            raw = self._call_gemini(prompt)
        except Exception as e:  # noqa: BLE001 - any failure must fall back cleanly
            logger.warning("Entity extraction failed, falling back: %s", e)
            return None

        parsed = self._parse_response(raw)
        if parsed is None:
            logger.warning("Could not parse entity extraction response; falling back")
            return None
        return parsed

    def _build_prompt(
        self,
        beats: List[Dict[str, str]],
        game: str,
        known_entities: Optional[List[str]],
    ) -> str:
        """Assemble the full prompt from instructions, entity list, and beats."""
        lines = [_SYSTEM_PROMPT.format(game=game), ""]
        if known_entities:
            lines.append(
                "Known entities in this game (prefer these exact names when "
                "the beat refers to one of them):"
            )
            lines.append(", ".join(known_entities))
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
                "temperature": 0.2,
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

    def _parse_response(self, raw: str) -> Optional[Dict[str, Dict]]:
        """Parse the model's JSON array into a beat-id -> classification mapping."""
        if not raw or not raw.strip():
            return None

        text = raw.strip()
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z]*\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

        try:
            items = json.loads(text)
        except json.JSONDecodeError:
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if not match:
                return None
            try:
                items = json.loads(match.group(0))
            except json.JSONDecodeError:
                return None

        if not isinstance(items, list):
            return None

        result: Dict[str, Dict] = {}
        for item in items:
            if not isinstance(item, dict):
                continue
            beat_id = item.get("id")
            if not beat_id:
                continue

            beat_class = (item.get("beat_class") or "").strip().lower()
            entities = item.get("entities")
            if not isinstance(entities, list):
                entities = []
            entities = [str(e).strip() for e in entities if str(e).strip()]

            # Keep class and entities consistent even if the model slips.
            if beat_class not in VALID_BEAT_CLASSES:
                beat_class = "game_entity" if entities else "abstract"
            if beat_class == "game_entity" and not entities:
                beat_class = "abstract"

            result[beat_id] = {"beat_class": beat_class, "entities": entities}

        return result or None
