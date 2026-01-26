# Markdown Script Guide

This guide explains how to write markdown scripts that work optimally with **ScreenWrite** for automatic B-roll generation and FCPXML timeline creation.

## Overview

ScreenWrite parses markdown files to create video timelines with automatic B-roll footage. The system analyzes your script content to:

1.  **Break text into beats**: 5-10 second segments based on word count.
2.  **Generate search queries**: Create stock footage and YouTube search terms.
3.  **Fetch B-roll assets**: Download relevant video clips automatically.
4.  **Create FCPXML timeline**: Generate a timeline ready for DaVinci Resolve.

---

## Script Structure

### Metadata
Start your script with metadata keys to provide high-level context.

```markdown
Title: Python Tutorial
Hook: Learn to code in 10 minutes.
Tags: python, coding, tutorial
```

### Basic Format
Use standard Markdown headers to define sections.

```markdown
# Main Title

## Section Header
Your script content goes here. Write naturally as you would speak in your video. 

[B-roll: close up of person typing]
The system will automatically break this into appropriate segments.
```

### Visual Instructions
You can explicitly request visuals using bracket notation. Place these **immediately before** the text they relate to.

| Action | Description | Example |
| :--- | :--- | :--- |
| `[B-roll: ...]` | Background video footage | `[B-roll: mountain sunset]` |
| `[Image: ...]` | Static images or screenshots | `[Image: software logo]` |
| `[Annotation: ...]` | On-screen text overlays | `[Annotation: "Tip #1"]` |
| `[Citation: ...]` | Source credits | `[Citation: Wikipedia]` |

---

## Timing and Beat Generation

The system uses a **2.5 words per second** heuristic to calculate timing.

- **13-25 words**: 5-10 second beat (optimal range).
- **Short segments**: Automatically merged.
- **Long segments**: Automatically split.

### Example
```markdown
## Installation
Visit the official Python website and download the latest version for your operating system.
```
*Word count: 15 words ≈ 6 seconds.*

---

## Best Practices

### ✅ DO
- **Be specific**: "Open Visual Studio Code" is better than "Open your editor."
- **Use active voice**: "Click the button" instead of "The button should be clicked."
- **Mention visual elements**: Reference colors, positions, and UI labels.
- **Write for the ear**: Read your script aloud to ensure it sounds natural.

### ❌ DON'T
- **Use abstract concepts**: "Logical thinking" is hard to fetch; "typing code" is easy.
- **Write long paragraphs**: Keep segments under 30 words for better pacing.
- **Include code blocks**: The parser ignores code blocks; describe the code instead.

---

## Testing Your Scripts

Use the CLI to test your script structure without downloading assets:

```bash
screenwrite your-script.md --output test.fcpxml --no-fetch --verbose
```

This will show you exactly how your script is segmented and what search queries are generated.