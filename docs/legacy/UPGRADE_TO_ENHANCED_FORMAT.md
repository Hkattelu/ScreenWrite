# Upgrading to Enhanced Markdown Format

This guide shows how to upgrade your existing markdown scripts to use the new enhanced format with B-roll instructions, metadata, and better structure support.

## What's New

### 1. **Metadata Support**

You can now add metadata at the top of your script:

```markdown
Title: My Video Title
Hook: Opening statement that hooks viewers
Channel: My Channel
Duration: 12:30
Tags: tutorial, programming, python
```

**Before (implicit context):**
```markdown
# Video Title About Something
# Programming Tutorial
...
```

**After (explicit metadata):**
```markdown
Title: Programming Tutorial for Beginners
Hook: Welcome to this programming tutorial!
...
```

### 2. **Inline B-Roll Instructions**

You can now explicitly specify what footage to show using `[action: content]` syntax.

**Before (implicit):**
```markdown
## Learning Python

Open Visual Studio Code and create a new Python file. The text editor will help you write better code.
```

The system had to guess that "Visual Studio Code" and "Python file" were visual elements to show.

**After (explicit):**
```markdown
## Learning Python

[Show: Visual Studio Code interface]
Open Visual Studio Code and create a new Python file.

[B-roll: person typing code]
The text editor will help you write better code.
```

### 3. **Improved Section Organization**

Use structured section types for better organization:

```markdown
Title: My Video

## Motivation

Why this topic matters...

## Hook

Opening statement...

## Content

### Section 1: First Topic

[Show: related footage]
Content about first topic...

### Section 2: Second Topic

Content about second topic...

## Call to Action

Final message...

## Sources

- Link and description
```

## Migration Steps

### Step 1: Add Metadata

At the very beginning of your script, add:

```markdown
Title: [Your video title]
Hook: [Your opening hook]
```

Optional:
```markdown
Channel: [Your channel name]
Duration: [estimated length like 12:30]
Tags: [comma-separated tags]
```

**Example:**
```markdown
Title: The Lost Art of Text-Based Game Walkthroughs
Hook: Welcome viewers. Today I'll be taking you through the history of an underappreciated art.
Channel: Gaming History
Tags: gaming, walkthroughs, retro, nostalgia

## Motivation

I want to discuss the past and present...
```

### Step 2: Add B-Roll Instructions

Find places where you want to explicitly show specific footage, and add instructions:

**Pattern:** `[action: what to show]`

Common actions:
- `[Show: ...]` - display content
- `[Display: ...]` - overlay/present
- `[Annotation: ...]` - on-screen text
- `[Screenshot: ...]` - software interface
- `[B-roll: ...]` - video footage
- `[ScreenWrite: ...]` - specific recording
- `[Interview: ...]` - interview clip
- `[Visual: ...]` - general reference

**Example:**

```markdown
## Early Walkthroughs

[Show: cover of "Mastering Pac-Man" book from 1981]
The earliest instances of walkthroughs came from physical books.

[Annotation: "First video game guidebook - 1981"]
These were carefully crafted with precision.

[Display: Nintendo Power magazine cover]
Later, official publications became popular.

[B-roll: person reading game guide while playing]
Players would reference guides as they played.
```

### Step 3: Reorganize Content (Optional)

If your script is long and complex, use special section headers:

```markdown
## Motivation
## Actual Title Options
## Hook
## Content
  ### Section 1
  ### Section 2
## Call to Action
## Sources
```

This helps organize different parts of your video.

### Step 4: Add Sources/Links

At the end, add a sources section:

```markdown
## Sources

- [Wikipedia](https://example.com) - Main reference
- [Historical Document](https://example.com/doc.pdf) - Source material
- [Related Video](https://youtube.com/watch?v=xxx) - Context
```

## Common Patterns

### Pattern 1: Simple Enhancement

**Before:**
```markdown
# Python Tutorial

First, install Python on your computer. Visit python.org and download the latest version.
```

**After:**
```markdown
Title: Python Installation Tutorial

## Setup

[Show: Python.org website]
First, install Python on your computer and visit python.org.

[Screenshot: Python download page]
Download the latest version for your operating system.
```

### Pattern 2: Complex Video with Sections

**Before:**
```markdown
# Game Walkthrough History

## Early Days
Old walkthroughs...

## Modern Era
New walkthroughs...

## Conclusion
Final thoughts...
```

**After:**
```markdown
Title: The History of Game Walkthroughs
Hook: Let me take you through the evolution of game guides
Channel: Gaming

## Motivation

Why game walkthroughs matter...

## Content

### Section 1: Early Era

[Show: vintage game walkthrough book]
Old walkthroughs were text-based...

[Display: arcade cabinet from 1980s]
Games came from arcades...

### Section 2: Modern Era

[Screenshot: GameFAQs website interface]
Today we use online guides...

[B-roll: YouTube walkthrough video]
Video guides are now popular...

## Call to Action

What's your favorite guide format? Let me know in the comments!

## Sources

- [Video Game Walkthrough - Wikipedia](https://en.wikipedia.org/wiki/Video_game_walkthrough)
- [GameFAQs Archives](https://gamefaqs.gamespot.com)
```

### Pattern 3: Using Annotations for Titles

If you have multiple title options, you can annotate them:

```markdown
Title: [Primary title]

## Actual Title Options

[Annotation: Option 1: The best title]
[Annotation: Option 2: Alternative title]
[Annotation: Option 3: Another option]
```

Or use a list:
```markdown
## Title Options

- The Best Title Option
- Alternative Title
- Another Great Title
```

## Compatibility

**Good news:** The enhanced format is **backwards compatible**. 

- Old scripts without metadata still work
- Scripts without B-roll instructions still work
- Scripts without special sections still work

You can upgrade gradually:
1. Start with just adding a Title
2. Then add Hook
3. Then start adding [Show: ...] instructions where useful
4. Organize sections when you have time

## Benefits of Upgrading

âœ… **Better B-Roll**: Explicit instructions mean more precise asset selection
âœ… **Clearer Intent**: Readers (and the parser) understand what you want shown
âœ… **Better Organization**: Metadata and sections make scripts more readable
âœ… **Future-Proof**: Parser improvements will better utilize these features
âœ… **Professional Structure**: Follows video production conventions

## Reference

For complete syntax details, see:
- [Enhanced Markdown Format Specification](MARKDOWN_SCRIPT_FORMAT.md) - Complete reference
- [Original Markdown Guide](MARKDOWN_SCRIPT_GUIDE.md) - Legacy format info

## Examples

### Before and After: Full Script

**BEFORE (Old Format):**
```markdown
# Python Tips and Tricks

## Getting Started

You should install Python if you haven't already. Go to python.org and download it.

Next, open your terminal and verify the installation by typing python --version.

## Advanced Features

Python has some amazing features like list comprehensions.

[code example would go here]

This makes your code more readable and efficient.

## Wrap Up

Now you know more about Python. Thanks for watching!
```

**AFTER (Enhanced Format):**
```markdown
Title: Python Tips and Tricks for Beginners
Hook: In this video, I'll show you some amazing Python features
Channel: Programming Tutorials
Tags: python, programming, tutorial

## Motivation

Python is one of the most popular programming languages. Whether you're just starting or looking to improve, these tips will help.

## Hook

In this video, I'll show you some amazing Python features that will make your code cleaner and more efficient.

## Content

### Getting Started

[Show: Python.org homepage]
First, you should install Python if you haven't already.

[Screenshot: Python download page with version options]
Go to python.org and download the latest version for your operating system.

[B-roll: terminal window with command prompt]
Open your terminal and verify the installation by typing python --version.

### Advanced Features

[Show: Python code editor with list comprehension example]
Python has some amazing features like list comprehensions.

[Annotation: "List comprehensions make code more readable"]
This makes your code more readable and efficient.

### Practical Example

[B-roll: developer typing Python code]
Let me show you a real-world example...

## Call to Action

What's your favorite Python feature? Let me know in the comments!

Don't forget to subscribe for more Python tips.

## Sources

- [Official Python Documentation](https://docs.python.org)
- [PEP 202 - List Comprehensions](https://www.python.org/dev/peps/pep-0202/)
```

## Questions?

If you have questions about the enhanced format:
1. Check the [MARKDOWN_SCRIPT_FORMAT.md](MARKDOWN_SCRIPT_FORMAT.md) specification
2. Look at examples in the docs/examples/ directory
3. Review the best practices section in the format guide

