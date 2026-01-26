# Markdown Cheat Sheet for Video Scripts

Quick reference for the enhanced markdown format.

## Metadata (Top of File)

```markdown
Title: Your Video Title
Hook: Opening hook that grabs attention
Channel: Your Channel Name
Duration: 12:30
Tags: tag1, tag2, tag3
```

## Headers (Organization)

```markdown
# Main Section (H1 - use rarely)
## Major Section (H2 - primary structure)
### Subsection (H3 - detailed sections)
```

## Content Instructions

```markdown
[Image: images, screenshots, diagrams, or UI]
[B-roll: video footage, interviews, or gameplay]
[Annotation: prominent on-screen text or labels]
[Citation: source attribution (bottom left corner)]
```

## Common Patterns

### Simple Content Block
```markdown
## Topic Name

[Image: relevant image or screenshot]
Main content text here...
```

### Multi-Instruction Section
```markdown
## Complex Topic

[Image: first visual element]
Introductory text...

[B-roll: video footage or interview]
More detailed explanation...

[Image: supporting image]
Final details...
```

### Section with Annotations and Citations
```markdown
## Historical Context

[Annotation: "Year: 1985"]
This happened in 1985 and it was important.

[Image: historical photograph or document]
Here's what it looked like.

[Citation: Wikipedia - Historical Events]
Documentation of this moment.
```

### Title Options
```markdown
## Actual Title Options

- Option 1: Main Title Here
- Option 2: Alternative Title
- Option 3: Another Possibility
```

## Full Structure Template

```markdown
Title: Video Title Here
Hook: Your compelling opening
Channel: Channel Name
Tags: relevant, tags

## Motivation

Why does this video matter?

## Actual Title Options

- Title option 1
- Title option 2
- Title option 3

## Hook

[Image: eye-catching image or screenshot]
Your opening statement that hooks viewers...

## Content

### Section 1: First Topic

[Image: relevant image]
Content for first section...

### Section 2: Second Topic

[B-roll: supporting video or interview]
Content for second section...

### Section 3: Third Topic

[Image: visual reference]
Content for third section...

[Citation: Source Name - source.com]

## Call to Action

[Annotation: "Like, Subscribe, Share"]
Final message and call to action...

## Sources

- [Reference Title](URL) - Description
- [Another Reference](URL) - More details
```

## Do's and Don'ts

### âœ… Do

- Use specific, visual descriptions
  ```markdown
  âœ… [Image: Python code in Visual Studio Code editor]
  ```

- Place instructions near relevant text
  ```markdown
  âœ… [Image: website homepage]
     Visit the website and click signup.
  ```

- Chain instructions logically
  ```markdown
  âœ… [Image: download button on website]
     [B-roll: file saving dialog animation]
     [Annotation: "Choose your location"]
  ```

- Use consistent instruction types
  ```markdown
  âœ… [Image: ...]
     [B-roll: ...]
     [Annotation: ...]
     [Citation: ...]
  ```

- Add citations for sources
  ```markdown
  âœ… [Citation: Wikipedia - Video Game History]
  ```

### âŒ Don't

- Be vague
  ```markdown
  âŒ [Image: stuff]
  âŒ [B-roll: things]
  ```

- Use wrong capitalization
  ```markdown
  âŒ [image: lowercase action]
  âŒ [IMAGE: ALL CAPS]
  âŒ Image: no brackets
  ```

- Leave orphaned instructions
  ```markdown
  âŒ [Image: random screenshot]
     [Complete tangent content]
  ```

- Over-instruct every sentence
  ```markdown
  âŒ [Image: something] Text here. [Image: another thing] More text.
  âŒ [B-roll: yet another] Final text.
  ```

## Word Count Guide

Target **13-25 words** per beat for 5-10 seconds:

```markdown
Too short (3 words):
"Open the terminal."

Good (14 words):
"Open your terminal application and navigate to your Documents folder using the cd command."

Too long (50 words):
"Open your terminal application, navigate to your Documents folder using the cd command, then create a new directory for your Python project files, and finally initialize a new Git repository with the git init command to enable version control."

Better (18 words):
"Open your terminal and navigate to Documents. Create a new folder and initialize a Git repository."
```

## Quick Examples

### Tutorial Script
```markdown
Title: Python Beginners Tutorial
Hook: Learn Python in 15 minutes!

## Content

### Installation

[Image: Python.org homepage]
Visit python.org and download the latest version.

[Image: installation wizard]
Run the installer and follow the prompts.

[Citation: Python.org - Official Download]

### Your First Program

[Image: Python code in editor]
Create a file called hello.py and type print("Hello World").

[B-roll: code editor executing program]
Run the script and see your message appear.
```

### Product Demo
```markdown
Title: Photoshop Basics Explained
Hook: Master Photoshop in one video

## Content

### Opening a File

[Image: File menu in Photoshop]
Click File, then Open to load your image.

[Image: file dialog with image selected]
Select your image and click Open.

### Basic Editing

[B-roll: cropping and resizing demonstration]
Use the crop tool to adjust your image composition.

[Citation: Adobe Photoshop Official Documentation]
```

### Game Walkthrough
```markdown
Title: [Game Name] Walkthrough

## Content

### Level 1

[Image: level map and overview]
Start at the beginning and move forward.

[Annotation: "Collect all coins for achievement"]
Pick up items as you go.

### Boss Fight

[B-roll: boss battle footage]
Dodge attacks and hit when you have openings.

[Annotation: "Weak spot: Back of head"]
Attack the glowing area for maximum damage.
```

### Educational Content
```markdown
Title: Understanding [Topic]
Hook: Let me explain [Topic] simply

## Motivation

Why this matters...

## Content

### Part 1: Basics

[Image: diagram of key concepts]
Here's the foundation...

### Part 2: Advanced

[B-roll: animated explanation or example]
Now let's apply it...

[Citation: Educational Source - edu.org]

## Call to Action

Questions? Comment below!
```

## Metadata Reference

| Key | Purpose | Example |
|-----|---------|---------|
| `Title` | Video title | `Python Basics Tutorial` |
| `Hook` | Opening statement | `Learn Python today` |
| `Channel` | Channel name | `Tech Tutorials` |
| `Duration` | Video length | `12:30` |
| `Tags` | Content categories | `python,tutorial,beginner` |

## Action Types

| Action | Use for | Example |
|--------|---------|---------|
| `Image` | Images, screenshots, diagrams, UI | `[Image: book cover from 1981]` |
| `B-roll` | Video footage, interviews, gameplay | `[B-roll: person coding]` |
| `Annotation` | Prominent on-screen text/labels | `[Annotation: "Est. 1950"]` |
| `Citation` | Source attribution (bottom left) | `[Citation: Wikipedia - History]` |

## Upgrade Checklist

- [ ] Add `Title` to top of script
- [ ] Add `Hook` with opening statement
- [ ] Add `Channel` if relevant
- [ ] Identify key visual moments
- [ ] Add `[Show: ...]` instructions where needed
- [ ] Add `[Annotation: ...]` for on-screen text
- [ ] Organize into Content sections
- [ ] Add Call to Action section
- [ ] Add Sources/References
- [ ] Review for word count per beat
- [ ] Test with parser

## Testing

Verify your script before processing:

```bash
# Test parsing without fetching assets
python -m screenwrite your_script.md --output test.fcpxml --no-fetch --verbose
```

Check for:
- âœ“ Proper metadata extraction
- âœ“ Valid beat generation
- âœ“ Correct instruction parsing
- âœ“ Appropriate word counts
- âœ“ Natural flow when read aloud

## Need Help?

- **Full Reference**: See `MARKDOWN_SCRIPT_FORMAT.md`
- **Migration Guide**: See `UPGRADE_TO_ENHANCED_FORMAT.md`
- **Complete Example**: See `examples/video_walkthroughs_enhanced.md`
- **Original Guide**: See `MARKDOWN_SCRIPT_GUIDE.md`

