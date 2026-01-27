# Specification: Beat Flavors UI Refinement

## Overview
Currently, the `BeatList` UI treats all beats as video assets, showing a video player or a "No Preview" spinner for every segment. This track introduces "Beat Flavors"—specialized UI treatments for **Annotation**, **Citation**, and **Image** beats—ensuring the interface reflects the semantic purpose of the Markdown syntax.

## Functional Requirements

### 1. Specialized Asset Slots
- Replace the generic video player with specialized "Asset Slots" based on the `visual_type` of the beat.
- **Annotation & Citation Beats**:
    - Use a **Minimalist Badge** approach.
    - Display a clear **Type Label** (e.g., "ANNOTATION" or "CITATION") and a corresponding icon.
    - Remove the video player and download spinner for these types.
- **Image Beats**:
    - Display a minimalist image placeholder icon.
    - Provide a visible **Upload Button** that triggers the native system file picker to select a local image.

### 2. Flavor-Specific Styling
- **Annotation**: Styled with purple accents (`bg-purple-50`, `text-purple-600`).
- **Citation**: Styled with amber accents (`bg-amber-50`, `text-amber-600`).
- **Image**: Styled with indigo accents (`bg-indigo-50`, `text-indigo-600`).

### 3. Data Integrity
- Ensure that editing a beat preserves its `visual_type` and `visual_content` in the frontend state and persists it to the backend.

## Non-Functional Requirements
- **Legibility**: All labels must use a minimum of 12px (`text-xs`) font size.
- **Accessibility**: All buttons and interactive badges must have descriptive `aria-label` attributes.
- **Consistency**: Maintain the "clean productivity" aesthetic of the existing ScreenWrite UI.

## Acceptance Criteria
- [ ] A beat with `[@Annotation: ...]` displays a purple "ANNOTATION" badge instead of a video player.
- [ ] A beat with `[@Citation: ...]` displays an amber "CITATION" badge.
- [ ] A beat with `[@Image: ...]` displays an indigo "IMAGE" badge with an upload button.
- [ ] Clicking the Image upload button opens the system file dialog.
- [ ] No "Downloading..." spinners appear for Annotation or Citation beats.

## Out of Scope
- Rich WYSIWYG previews (rendering text overlays on top of images/colors).
- Real-time fetching of images via API (Pexels, etc.) for this track.
