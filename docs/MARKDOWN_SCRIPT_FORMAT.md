# Enhanced Markdown Script Format for vid-orchestrator

This document specifies the robust markdown flavor for video scripts with B-roll generation support.

## Overview

The enhanced format supports:
- **Structured metadata** (title, hook, sections)
- **Inline B-roll instructions** (visual cues and asset references)
- **Content annotations** (on-screen text, callouts)
- **Section organization** (logical grouping for video structure)
- **Link references** (external sources and citations)

## Core Syntax

### Top-Level Metadata

At the beginning of the script, define metadata using `key: value` pairs:

```markdown
Title: The lost art of text-based game walkthroughs
Hook: Welcome viewers. Today i'll be taking you through the history...
Duration: 12:30
Channel: Gaming History
```

**Supported metadata keys:**
- `Title` - Video title (primary context for B-roll)
- `Hook` - Opening/hook statement
- `Channel` - Channel name
- `Duration` - Estimated video length
- `Thumbnail` - Thumbnail concept/text
- `Tags` - Content tags for relevance

### Headers (Section Division)

Use markdown headers to organize content:

```markdown
# Main Section
## Subsection
### Minor heading
```

Headers provide **context** that influences B-roll selection for all following beats.

### Body Text (Beats)

Regular text becomes video beats (5-10 second segments):

```markdown
## Section Title

This is body text that will be chunked into beats automatically. Write naturally as you would speak.
```

### Inline B-Roll Instructions

Specify visual assets to show using bracket notation:

#### Basic Instruction Format

```
[action: description]
```

**Supported actions:**

| Action | Purpose | Example |
|--------|---------|---------|
| `Image` | Display images, screenshots, UI, or visual content | `[Image: screenshots of game menus]` |
| `B-roll` | Video footage or recordings (includes interviews and gameplay) | `[B-roll: people playing retro games]` |
| `Annotation` | Prominent on-screen text/labels | `[Annotation: "Est. 1981"]` |
| `Citation` | Source attribution in bottom left corner | `[Citation: Wikipedia - Video Game Walkthrough]` |

#### Examples

```markdown
[Image: old text-based walkthrough guide]
The walkthrough format has changed dramatically over the years.

[Annotation: "1981 - First video game guidebook"]
The earliest instances of walkthroughs came from physical books.

[B-roll: person reading guide book at desk]
These guides were carefully crafted with precision.

[Image: GameFAQs.com interface with multiple guides listed]
The internet changed everything about how we access walkthroughs.

[Citation: GameFAQs Archive - https://gamefaqs.gamespot.com]
Community-written guides became the standard resource.
```

#### Grouped Instructions

Combine multiple instructions together:

```markdown
[Image: screenshots of Jak&Daxter, FF12, FF10 walkthroughs]

[Image: multiple browser tabs with different guides]
[Annotation: "Est. 2000s - Peak of text-based walkthroughs"]
```

### Inline Annotations

Add contextual notes within text using parentheses:

```markdown
The Nintendo Power Hotline (1987-2005) was a groundbreaking service.
(on screen: show hotline advertisement)
```

### Section Types

Use special section markers for different content areas:

```markdown
## Motivation

Why this topic matters...

## Actual Title Options

- Title option 1
- Title option 2
- Title option 3

## Hook

Opening statement that hooks the viewer...

## Content

Main body of the video...

### Section 1: Topic

[Show: relevant footage]
Content for this section...

### Section 2: Another Topic

Content continues...

## Call to Action

Final message to viewers...

## Sources / References

- Link 1: description
- Link 2: description
```

## Advanced Features

### Links and References

Embed clickable links with context:

```markdown
## References

[View Full Guide](https://example.com/guide)
[PDF Source](https://example.com/document.pdf)
[Watch Related Video](https://youtube.com/watch?v=xxx)
```

### Lists for Alternative Content

Use lists to show options (for metadata like titles or footage options):

```markdown
## Actual Title

Option 1: The Lost Art of Text-Based Game Walkthroughs
Option 2: GameFAQs, Guidebooks, and Hotlines
Option 3: Why Old-School Walkthroughs Were Better
Option 4: Game Walkthroughs Used to Be AMAZING
```

Or as unordered lists:

```markdown
## Thumbnail Options

- These were amazing
- A lost art
- Everything changed
```

### Nested Beats

Break up complex sections with sub-headers:

```markdown
## Main Topic

Introduction to main topic...

### Subtopic A

[Show: related footage]
Details about subtopic A...

### Subtopic B

More details about subtopic B...
```

## Parsing Rules

### Text Processing

1. **Headers** extracted as context
2. **Body text** chunked into 5-10 second beats using word count (2.5 words/second)
3. **B-roll instructions** extracted as metadata for beats
4. **Links** preserved for reference
5. **Lists** converted to text or extracted as alternatives

### B-Roll Instruction Handling

Each instruction is parsed into:
- **Action type** (Show, Display, Annotation, etc.)
- **Subject/content** (what to show)
- **Associated beat** (which text segment it accompanies)

### Beat Generation

Beats are generated from body text, with B-roll instructions either:
- **Attached to preceding text** if they immediately follow
- **Linked to nearest beat** if separated by blank lines
- **Standalone** if surrounded by whitespace

### Search Query Generation

For each beat, the system generates:
1. **Stock footage keyword** - for Pexels/stock libraries
2. **YouTube search phrase** - for YouTube content
3. **B-roll instruction** - from inline `[...]` directives

When B-roll instructions are present, they **override** auto-generated queries.

## Examples

### Simple Example

```markdown
Title: Python Basics

Hook: In this video, we'll learn Python from scratch.

## Getting Started

[Image: Python logo and website]
First, you need to install Python on your computer.

[Annotation: "Python 3.12 recommended"]
Visit the official Python website and download the latest version.

## Your First Program

[B-roll: person typing in text editor]
Create a new file called hello.py and type your first program.

[Image: code appearing on screen]
The basic "Hello World" program demonstrates how to print text.
```

### Complex Example (Like Your Script)

```markdown
Title: The Lost Art of Text-Based Game Walkthroughs

Hook: Welcome viewers. Today I'll be taking you through the history of an underappreciated art.

## Motivation

I want to discuss the past and present of video game walkthroughs...

## Content

### Section 1: Guide Books and Hotlines

[Image: cover of "Mastering Pac-Man" book]
The earliest instances of walkthroughs came from 1981...

[Image: vintage arcade machine]
The arcade culture of the early 80s shaped gaming help...

[Image: Nintendo Power hotline advertisement]
The Nintendo Power Hotline ran from 1987 to 2005...

[B-roll: interview clip with former Nintendo counselor]
Real-time feedback was a game-changer for players...

[Citation: Nintendo Power Archives - archive.org]
Historical documentation of the hotline service.

### Section 2: Rise of Internet Walkthroughs

[Image: GameFAQs.com with multiple guides]
When I was growing up, my favorite walkthroughs were text-based...

[Image: Cheatcodes.com homepage layout]
These sites hosted thousands of community-written guides...

[B-roll: person using Ctrl+F to search in guide]
The searchability of text-based guides was revolutionary...

[Citation: GameFAQs Archive - https://gamefaqs.gamespot.com]

## Call to Action

What's your favorite walkthrough format? Let me know in the comments!

## Sources

- [Wikipedia: Video Game Walkthrough](https://en.wikipedia.org/wiki/Video_game_walkthrough)
- [GameFAQs Archive](https://gamefaqs.gamespot.com)
- [Nintendo Power History](https://archive.org/details/nintendopower)
```

## Best Practices

### Do's

✅ Use **specific subject names** in instructions
```markdown
✅ [Image: Nintendo Power magazine cover from 1990]
❌ [Image: old magazine]
```

✅ **Chain instructions** for logical sequences
```markdown
[Image: person booting up computer]
[Image: Windows 95 startup animation]
[B-roll: dialup modem connecting]
The dial-up era was slow but magical...
```

✅ Use **action-oriented language** in body text
```markdown
✅ "Navigate to the GameFAQs website and search for your game"
❌ "Look up information about your game"
```

✅ Place instructions **near related text**
```markdown
[Image: old arcade cabinet]
Arcade cabinets of the 80s didn't come with instructions...
```

✅ Use **Citation** for source attribution
```markdown
[Citation: Wikipedia - Video Game Walkthrough]
```

### Don'ts

❌ Vague instructions
```markdown
❌ [Image: stuff]
❌ [B-roll: things from the past]
```

❌ Orphaned instructions (disconnected from text)
```markdown
❌ [Image: random screenshot]
❌ [B-roll: something]
Text that has nothing to do with above...
```

❌ Over-instructing
```markdown
❌ Every sentence has a [Image: ...] instruction
```

❌ Mixing instruction formats
```markdown
❌ [image: lowercase]
❌ Image: without brackets
```

## Markdown Validation

Valid markdown should:
1. Have a `Title` metadata line
2. Use `# or ##` for section headers
3. Include body text for beats
4. Use consistent `[action: content]` instruction format
5. Not have orphaned or incomplete instructions

## File Encoding

- **Recommended**: UTF-8
- **Supported**: UTF-8, ASCII, Latin-1
- **Line endings**: LF (\n) or CRLF (\r\n)

## Compatibility

This format is designed to:
- **Parse naturally** as readable markdown
- **Generate searchable queries** for B-roll assets
- **Map to FCPXML** timeline structure
- **Support manual override** of auto-generated content
