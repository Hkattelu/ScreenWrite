"""
Provenance notes for placed clips: which source, which labeled moment, where.

Shared by the FCPXML generator (clip markers) and the native Resolve builder
(timeline marker notes) so a clip is identifiable at a glance during VO work
without re-watching it.
"""

from typing import Optional

from ..core.beat import Beat


def build_provenance_note(beat: Beat, asset_path: str) -> Optional[str]:
    """
    Build a provenance note for the candidate that produced asset_path.

    Includes the source label, the human-authored chapter/page label with
    its source timestamp, the source URL, and any alternate candidate URLs
    (the web state keeps full alternates; the note keeps them reachable
    from inside the editor).
    """
    placed = None
    alternates = []
    for candidate in beat.candidates:
        if candidate.get('local_path') == asset_path and placed is None:
            placed = candidate
        else:
            alternates.append(candidate)
    if placed is None:
        return None

    metadata = placed.get('metadata') or {}
    parts = [f"Source: {placed.get('source', 'unknown')}"]
    chapter_title = metadata.get('chapter_title') or metadata.get('title')
    if chapter_title:
        timestamp = metadata.get('segment_start')
        if timestamp is not None:
            parts.append(f"'{chapter_title}' @ {int(timestamp)}s")
        else:
            parts.append(f"'{chapter_title}'")
    source_url = metadata.get('source_url') or metadata.get('url')
    if source_url:
        parts.append(source_url)
    alternate_urls = [
        (c.get('metadata') or {}).get('source_url')
        for c in alternates
        if (c.get('metadata') or {}).get('source_url')
    ]
    if alternate_urls:
        parts.append("Alternates: " + " ; ".join(alternate_urls[:2]))
    return " | ".join(parts)
