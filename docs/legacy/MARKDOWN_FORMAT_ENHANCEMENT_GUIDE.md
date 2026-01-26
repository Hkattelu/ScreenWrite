# Markdown Format Enhancement - Quick Start Guide

Your markdown syntax has been enhanced to support more robust video scripts. Here's what's new and how to use it.

## TL;DR - The Three Changes

### 1. Add Metadata at the Top
```markdown
Title: Your Video Title
Hook: Your opening hook
```

### 2. Add B-Roll Instructions Where Needed
```markdown
[Show: something specific]
Your content text...
```

### 3. Organize into Sections (Optional)
```markdown
## Content
### Topic 1
### Topic 2
## Call to Action
```

That's it. Your old scripts still work without these.

---

## What Each Feature Does

### Metadata (Optional)
```markdown
Title: Python Basics Tutorial
Hook: Learn Python in 15 minutes
Channel: Tech Education
Duration: 15:00
Tags: python, tutorial, beginner
```

**Purpose**: Provides context for the entire video to improve B-roll accuracy.

### B-Roll Instructions (Optional)
```markdown
[Show: Visual Studio Code interface]
[Display: error message dialog]
[Annotation: "Import the library first"]
[Screenshot: command line output]
[B-roll: person typing code]
[Footage: video clip of installation]
[Interview: expert discussing best practices]
[Visual: relevant concept diagram]
```

**Purpose**: Explicitly specify what to show for each beat. Overrides auto-generated search queries.

### Section Organization (Optional)
```markdown
## Motivation - Why this matters
## Actual Title Options - Possible titles
## Hook - Opening
## Content - Main video
  ### Section 1
  ### Section 2
## Call to Action - Engagement
## Sources - References
```

**Purpose**: Professional structure aligned with video production standards.

---

## Quick Examples

### Example 1: Minimal Enhancement
**Before:**
```markdown
# Python Tutorial

Open Visual Studio Code and create a new file.
```

**After:**
```markdown
Title: Python Tutorial

[Show: Visual Studio Code interface]
Open Visual Studio Code and create a new file.
```

### Example 2: Full Enhancement
**Before:**
```markdown
# Game Walkthroughs: Then and Now

The early walkthroughs were books. Modern ones are videos. Text-based guides are better for quick answers.
```

**After:**
```markdown
Title: The Lost Art of Text-Based Game Walkthroughs
Hook: Let me take you through the evolution of game guides

## Motivation
The early walkthroughs were books...

## Content

### Historical Era
[Show: vintage game guidebook]
The early walkthroughs were books...

### Modern Era
[Display: YouTube video interface]
Modern ones are videos...

### My Preference
[Visual: text document on screen]
Text-based guides are better for quick answers.

## Call to Action
What's your favorite guide format? Comment below!

## Sources
- [Wikipedia: Video Game Walkthrough](https://en.wikipedia.org/...)
```

---

## File Structure Reference

### Minimal Viable Script
```markdown
Title: Your Title

## Content

Your content here...
```

### Recommended Script
```markdown
Title: Your Title
Hook: Your opening statement

## Content

### Topic 1
[Show: relevant footage]
Content...

### Topic 2
[Display: supporting material]
More content...

## Call to Action
Final message...
```

### Full-Featured Script
```markdown
Title: Your Title
Hook: Your opening hook
Channel: Your Channel
Duration: 12:30
Tags: relevant, tags

## Motivation
Why this video matters...

## Actual Title Options
- Option 1
- Option 2
- Option 3

## Hook
[Show: attention-grabbing footage]
Your opening...

## Content

### Section 1
[Show: first topic imagery]
Content about section 1...

### Section 2
[Display: relevant content]
Content about section 2...

### Section 3
[B-roll: supporting footage]
Content about section 3...

## Call to Action
[Annotation: "Subscribe now"]
Final engagement message...

## Sources
- [Reference](URL) - Description
- [Another Reference](URL) - Details
```

---

## B-Roll Action Types

| Action | What It Means | When to Use |
|--------|--------------|------------|
| `[Show: ...]` | Display image/photo/footage | Most common, default choice |
| `[Display: ...]` | Present/overlay content | UI screens, magazine pages |
| `[Annotation: ...]` | Add on-screen text | Dates, titles, highlights |
| `[Screenshot: ...]` | Software interface | Code editor, website |
| `[B-roll: ...]` | Background video footage | People working, processes |
| `[Footage: ...]` | Specific video recording | Movie clips, recordings |
| `[Interview: ...]` | Interview or discussion | People talking/speaking |
| `[Visual: ...]` | General visual reference | Diagrams, illustrations |

---

## Migration Checklist

Start here and upgrade gradually:

**Step 1: Add Title**
- [ ] Add one line at top: `Title: Your title`
- [ ] Test parsing
- [ ] Keep everything else the same

**Step 2: Add Hook** (Optional)
- [ ] Add: `Hook: Your opening statement`
- [ ] Test parsing

**Step 3: Add Obvious Instructions** (Optional)
- [ ] Find 3-5 places where you want specific footage shown
- [ ] Add: `[Show: specific description]` before that text
- [ ] Test parsing

**Step 4: Reorganize** (Optional)
- [ ] Break into Motivation, Content, Call to Action sections
- [ ] Add subsections under Content
- [ ] Test parsing

**Step 5: Complete** (Optional)
- [ ] Add Channel, Duration, Tags
- [ ] Add more specific instructions
- [ ] Add Sources section

Each step is optional. You can stop at any point.

---

## Common Patterns

### Tutorial Script
```markdown
Title: [Technology] Tutorial: [Topic]
Hook: Learn [topic] in [time]

## Motivation
Why learn this?

## Content

### Setup
[Show: required tools/software]
Installation and setup instructions...

### First Example
[B-roll: demonstration]
Walking through basic example...

### Advanced
[Display: complex example]
More advanced techniques...

## Call to Action
Practice these techniques and subscribe!

## Sources
- [Reference]
```

### Product Review
```markdown
Title: [Product] Review
Hook: Is [product] worth it?

## Motivation
Why this product matters...

## Content

### Overview
[Show: product in use]
What is it...

### Features
[Display: key feature 1]
How feature 1 works...

[Display: key feature 2]
How feature 2 works...

### Pros & Cons
[Annotation: "Pros"]
Advantages...

[Annotation: "Cons"]
Disadvantages...

## Call to Action
Should you buy it? Let me know in comments!
```

### Entertainment Video
```markdown
Title: [Topic] Explained
Hook: [Compelling hook]

## Motivation
Why this topic is interesting...

## Content

### History
[Show: historical footage]
Background and history...

### Modern Era
[Display: current examples]
How it is today...

### My Take
[B-roll: commentary]
My personal perspective...

## Call to Action
What do you think? Comment your opinion!
```

---

## Syntax Rules

### Do's
✅ Use consistent capitalization: `[Show: ...]`, `[Display: ...]`  
✅ Be specific: `[Show: Pac-Man arcade cabinet from 1982]`  
✅ Place instructions near related text  
✅ Use brackets: `[` and `]`  
✅ Use colon: `:` between action and content  

### Don'ts
❌ Don't use lowercase: `[show: ...]` (wrong capitalization)  
❌ Don't be vague: `[Show: stuff]`  
❌ Don't forget brackets: `Show: content`  
❌ Don't forget colon: `[Show content]`  
❌ Don't orphan instructions (no related text nearby)  

### Valid Examples
```markdown
✅ [Show: Python.org homepage]
✅ [Display: IDE setup window]
✅ [Annotation: "Step 1 of 5"]
✅ [B-roll: developer typing code]
✅ [Screenshot: command line output]
```

### Invalid Examples
```markdown
❌ [show: lowercase]
❌ [SHOW: ALL CAPS]
❌ Show: no brackets
❌ [Show content without colon]
❌ [Show: ] (empty content)
```

---

## Word Count Tips

Target **13-25 words per beat** for 5-10 second segments:

```markdown
Too short (6 words):
"Install Python from the website."

Good (14 words):
"Visit the Python website and download the latest version for your operating system."

Too long (40 words):
"Visit the official Python website, click on the download button, select the version matching your operating system, wait for the file to download, and then double-click the installer to begin the installation process."

Better (16 words):
"Visit Python.org and download the installer for your operating system. Run the installer to complete setup."
```

---

## Testing Your Script

### Verify syntax is correct
```bash
# Parse without fetching assets
python -m vid_orchestrator your_script.md --output test.fcpxml --no-fetch --verbose
```

### Check for common issues
- ✓ Metadata appears at top (no blank lines before Title)
- ✓ Instructions use `[Action: content]` format
- ✓ Instructions have proper capitalization
- ✓ Each beat is 13-25 words
- ✓ Script reads naturally when spoken aloud

---

## Documentation Reference

| Document | Purpose |
|----------|---------|
| `docs/MARKDOWN_SCRIPT_FORMAT.md` | Complete spec (600+ lines) |
| `docs/MARKDOWN_CHEAT_SHEET.md` | Quick reference card |
| `docs/UPGRADE_TO_ENHANCED_FORMAT.md` | Detailed migration guide |
| `docs/ENHANCEMENTS_SUMMARY.md` | Feature overview |
| `examples/video_walkthroughs_enhanced.md` | Full working example |

---

## FAQ

**Q: Do I have to use the new format?**  
A: No. Your old scripts work exactly as before.

**Q: Can I mix old and new?**  
A: Yes. Some scripts can use new features while others use old format.

**Q: What if I get the syntax wrong?**  
A: Instructions won't be parsed, but your script still works (falls back to auto-generation).

**Q: Should I upgrade existing scripts?**  
A: Only if you want better control over B-roll. Not required.

**Q: Which action should I use?**  
A: Most content uses `[Show: ...]`. Use `[Annotation: ...]` for on-screen text.

**Q: Can I add my own action types?**  
A: Currently: Show, Display, Annotation, Screenshot, B-roll, Footage, Interview, Visual. Others will be parsed but not specially handled.

---

## Getting Help

1. **Quick answer?** → Check this file
2. **Full reference?** → See `docs/MARKDOWN_SCRIPT_FORMAT.md`
3. **Examples?** → See `examples/video_walkthroughs_enhanced.md`
4. **Step-by-step?** → Read `docs/UPGRADE_TO_ENHANCED_FORMAT.md`
5. **Quick lookup?** → Use `docs/MARKDOWN_CHEAT_SHEET.md`

---

## Summary

The markdown format is now more powerful while staying backwards compatible:

- **Add metadata** to provide context (optional)
- **Add B-roll instructions** for explicit control (optional)
- **Organize with sections** for professional structure (optional)
- **Your old scripts still work** without any changes

Start with just adding a `Title:` line and upgrade at your own pace.

---

**Status**: ✅ Ready to use  
**Compatibility**: ✅ 100% backwards compatible  
**Examples**: ✅ Provided  
**Documentation**: ✅ Complete
