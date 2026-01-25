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

## B-Roll Instructions

```markdown
[Show: specific footage or image]
[Display: overlay or presentation]
[Annotation: on-screen text or label]
[Screenshot: software interface or UI]
[B-roll: video footage or recording]
[Footage: specific video clip]
[Interview: interview or discussion clip]
[Visual: general visual reference]
```

## Common Patterns

### Simple Content Block
```markdown
## Topic Name

[Show: relevant footage]
Main content text here...
```

### Multi-Instruction Section
```markdown
## Complex Topic

[Show: first visual element]
Introductory text...

[Display: second visual element]
More detailed explanation...

[B-roll: supporting footage]
Final details...
```

### Section with Annotations
```markdown
## Historical Context

[Annotation: "Year: 1985"]
This happened in 1985 and it was important.

[Show: historical photograph or document]
Here's what it looked like.
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

[Show: eye-catching footage]
Your opening statement that hooks viewers...

## Content

### Section 1: First Topic

[Show: relevant visuals]
Content for first section...

### Section 2: Second Topic

[Display: related content]
Content for second section...

### Section 3: Third Topic

[B-roll: supporting footage]
Content for third section...

## Call to Action

[Annotation: "Like, Subscribe, Share"]
Final message and call to action...

## Sources

- [Reference Title](URL) - Description
- [Another Reference](URL) - More details
```

## Do's and Don'ts

### ✅ Do

- Use specific, visual descriptions
  ```markdown
  ✅ [Show: Python code in Visual Studio Code editor]
  ```

- Place instructions near relevant text
  ```markdown
  ✅ [Show: website homepage]
     Visit the website and click signup.
  ```

- Chain instructions logically
  ```markdown
  ✅ [Show: download button]
     [Display: file saving dialog]
     [Annotation: "Choose your location"]
  ```

- Use consistent action verbs
  ```markdown
  ✅ [Show: ...]
     [Display: ...]
     [Annotation: ...]
  ```

### ❌ Don't

- Be vague
  ```markdown
  ❌ [Show: stuff]
  ❌ [Display: things]
  ```

- Use wrong capitalization
  ```markdown
  ❌ [show: lowercase action]
  ❌ [SHOW: ALL CAPS]
  ❌ Show: no brackets
  ```

- Leave orphaned instructions
  ```markdown
  ❌ [Show: random footage]
     [Complete tangent content]
  ```

- Over-instruct every sentence
  ```markdown
  ❌ [Show: something] Text here. [Show: another thing] More text.
  ❌ [Show: yet another] Final text.
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

[Show: Python.org homepage]
Visit python.org and download the latest version.

[Screenshot: installation wizard]
Run the installer and follow the prompts.

### Your First Program

[Display: Python code on screen]
Create a file called hello.py and type print("Hello World").

[B-roll: code editor with output]
Run the script and see your message appear.
```

### Product Demo
```markdown
Title: Photoshop Basics Explained
Hook: Master Photoshop in one video

## Content

### Opening a File

[Show: File menu in Photoshop]
Click File, then Open to load your image.

[Screenshot: file dialog]
Select your image and click Open.

### Basic Editing

[B-roll: cropping and resizing demonstration]
Use the crop tool to adjust your image composition.
```

### Game Walkthrough
```markdown
Title: [Game Name] Walkthrough

## Content

### Level 1

[Show: level map or overview]
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

[Show: diagram of key concepts]
Here's the foundation...

### Part 2: Advanced

[Display: complex example]
Now let's apply it...

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
| `Show` | Display images/footage | `[Show: book cover from 1981]` |
| `Display` | Present content/overlay | `[Display: magazine page]` |
| `Annotation` | On-screen text/labels | `[Annotation: "Est. 1950"]` |
| `Screenshot` | Software/UI interfaces | `[Screenshot: Gmail inbox]` |
| `B-roll` | Supporting video footage | `[B-roll: person coding]` |
| `Footage` | Specific video recording | `[Footage: interview clip]` |
| `Interview` | Interview or discussion | `[Interview: expert talking]` |
| `Visual` | General visual reference | `[Visual: sunset landscape]` |

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
python -m vid_orchestrator your_script.md --output test.fcpxml --no-fetch --verbose
```

Check for:
- ✓ Proper metadata extraction
- ✓ Valid beat generation
- ✓ Correct instruction parsing
- ✓ Appropriate word counts
- ✓ Natural flow when read aloud

## Need Help?

- **Full Reference**: See `MARKDOWN_SCRIPT_FORMAT.md`
- **Migration Guide**: See `UPGRADE_TO_ENHANCED_FORMAT.md`
- **Complete Example**: See `examples/video_walkthroughs_enhanced.md`
- **Original Guide**: See `MARKDOWN_SCRIPT_GUIDE.md`
