# Markdown Script Guide for vid-orchestrator

This guide explains how to write markdown scripts that work optimally with vid-orchestrator for automatic B-roll generation and FCPXML timeline creation.

**⚠️ Enhanced Format Available**: This project now supports a more robust markdown flavor with B-roll instructions, metadata, and better structure. See [MARKDOWN_SCRIPT_FORMAT.md](MARKDOWN_SCRIPT_FORMAT.md) for the latest specification.

## Overview

vid-orchestrator parses markdown files to create video timelines with automatic B-roll footage. The system analyzes your script content to:

1. **Break text into beats** - 5-10 second segments based on word count
2. **Generate search queries** - Create stock footage and YouTube search terms
3. **Fetch B-roll assets** - Download relevant video clips automatically
4. **Create FCPXML timeline** - Generate a timeline ready for DaVinci Resolve

## Script Structure

### Basic Format

```markdown
# Main Title

## Section Header

Your script content goes here. Write naturally as you would speak in your video. The system will automatically break this into appropriate segments for B-roll placement.

## Another Section

Continue with more content. Each paragraph or section will be analyzed for relevant visual keywords.
```

### Key Principles

1. **Write conversationally** - Use natural speech patterns
2. **Include visual keywords** - Mention concrete objects, actions, and concepts
3. **Use descriptive language** - Help the system understand what visuals would be relevant
4. **Structure with headers** - Use `#` and `##` to organize content sections

## Timing and Beat Generation

### Word Count Guidelines

The system uses a **2.5 words per second** heuristic to calculate timing:

- **13-25 words** = 5-10 second beat (optimal range)
- **Shorter segments** may be combined with adjacent text
- **Longer segments** will be automatically split

### Example Beat Breakdown

```markdown
## Getting Started with Python

First, you need to install Python on your computer. Visit the official Python website and download the latest version for your operating system.
```

This becomes **2 beats**:
- Beat 1: "First, you need to install Python on your computer." (10 words ≈ 4 seconds)
- Beat 2: "Visit the official Python website and download the latest version for your operating system." (15 words ≈ 6 seconds)

## Optimizing for B-Roll Generation

### Include Visual Keywords

The system generates two types of search queries for each beat:

1. **Stock Keywords** - For stock footage libraries (Pexels)
2. **YouTube Phrases** - For YouTube content searches

#### Good Examples

```markdown
# Coding Tutorial

Open your favorite text editor or IDE like Visual Studio Code. We'll start by creating a simple "Hello World" program in Python.

Navigate to the terminal window and type the following command to run your script. You should see the output displayed in the console.
```

**Generated queries might include:**
- Stock: "text editor", "programming", "code typing"
- YouTube: "Visual Studio Code tutorial", "Python Hello World", "terminal command"

#### What Works Well

- **Specific software names**: "Visual Studio Code", "Photoshop", "Chrome"
- **Concrete actions**: "typing", "clicking", "installing", "downloading"
- **Visible objects**: "keyboard", "screen", "mouse", "computer"
- **Technical terms**: "terminal", "code", "website", "application"

### Avoid Abstract Concepts

Less effective for B-roll generation:
```markdown
# Philosophy of Programming

Programming is fundamentally about problem-solving and logical thinking. It requires patience, persistence, and creativity to develop elegant solutions.
```

Better approach:
```markdown
# Learning to Code

Start by opening your code editor and creating a new file. Practice writing simple programs that solve everyday problems, like calculating tips or organizing your music library.
```

## Content Guidelines

### Headers and Structure

Use headers to provide context that influences B-roll selection:

```markdown
# Web Development Tutorial

## Setting Up Your Environment

Download and install Node.js from the official website. Open your terminal and verify the installation by typing 'node --version'.

## Creating Your First Project

Navigate to your project folder and initialize a new Node.js project. Create an index.html file and open it in your browser.
```

Headers like "Web Development Tutorial" and "Setting Up Your Environment" provide context that helps generate more relevant search queries.

### Writing Style Tips

1. **Be specific about tools and technologies**
   ```markdown
   ✅ "Open Visual Studio Code and create a new Python file"
   ❌ "Open your editor and create a new file"
   ```

2. **Mention visual elements**
   ```markdown
   ✅ "Click the green 'Run' button in the toolbar"
   ❌ "Execute the program"
   ```

3. **Include step-by-step actions**
   ```markdown
   ✅ "Right-click on the desktop and select 'New Folder'"
   ❌ "Create a new folder"
   ```

4. **Reference UI elements**
   ```markdown
   ✅ "In the sidebar, expand the 'Files' panel"
   ❌ "Look at the file structure"
   ```

## File Organization

### Recommended Structure

```
project/
├── scripts/
│   ├── tutorial-intro.md
│   ├── setup-guide.md
│   └── advanced-topics.md
├── output/
│   ├── tutorial-intro.fcpxml
│   └── assets/
└── README.md
```

### Naming Conventions

- Use descriptive filenames: `python-basics-tutorial.md`
- Avoid spaces: use hyphens or underscores
- Keep names concise but clear

## Common Patterns

### Tutorial Structure

```markdown
# [Technology] Tutorial: [Topic]

## Introduction
Brief overview of what you'll learn and why it's useful.

## Prerequisites
What viewers need before starting (software, knowledge, etc.).

## Step 1: [Action]
Detailed instructions with specific steps and visual cues.

## Step 2: [Next Action]
Continue with logical progression.

## Troubleshooting
Common issues and solutions.

## Conclusion
Summary and next steps.
```

### Product Demo Structure

```markdown
# [Product Name] Demo: [Feature]

## Overview
What the product does and key benefits.

## Getting Started
How to access and initial setup.

## Key Features
Demonstrate main functionality with specific actions.

## Use Cases
Real-world examples and scenarios.

## Wrap Up
Summary and call-to-action.
```

## Best Practices

### Do's

- ✅ Write as you would speak in the video
- ✅ Include specific software, website, and tool names
- ✅ Mention visual elements (buttons, menus, windows)
- ✅ Use action verbs (click, type, drag, select)
- ✅ Reference colors, positions, and UI elements
- ✅ Keep sections focused on single topics
- ✅ Use consistent terminology throughout

### Don'ts

- ❌ Write overly long paragraphs (>50 words)
- ❌ Use only abstract concepts without visual elements
- ❌ Include complex formatting (tables, code blocks)
- ❌ Write in passive voice exclusively
- ❌ Use vague references ("this", "that", "it")
- ❌ Include placeholder text like "[TODO]"

## Troubleshooting

### If Beats Are Too Short

**Problem**: Generated beats are under 5 seconds
**Solution**: Write longer sentences or combine related ideas

```markdown
❌ "Install Python. Open the terminal. Run the command."
✅ "Install Python from the official website, then open your terminal and run the python --version command to verify the installation."
```

### If Beats Are Too Long

**Problem**: Generated beats exceed 10 seconds
**Solution**: Break complex ideas into simpler sentences

```markdown
❌ "Navigate to the Python website, download the installer for your operating system, run the installation wizard, accept the license agreement, choose your installation directory, and wait for the process to complete."
✅ "Navigate to the Python website and download the installer for your operating system. Run the installation wizard and follow the prompts to complete the setup."
```

### If B-Roll Queries Are Generic

**Problem**: Generated search terms are too vague
**Solution**: Include more specific visual keywords

```markdown
❌ "We'll work on the project now."
✅ "Open Visual Studio Code and create a new React project using the terminal."
```

## Testing Your Scripts

Before running the full pipeline, you can test your script structure:

1. **Check word count**: Aim for 13-25 words per intended beat
2. **Review for visual keywords**: Ensure each paragraph mentions concrete, visual elements
3. **Read aloud**: Does it sound natural when spoken?
4. **Verify specificity**: Are tool names, actions, and UI elements clearly mentioned?

Use the `--no-fetch` flag to test script parsing without downloading assets:

```bash
python -m vid_orchestrator your-script.md --output test.fcpxml --no-fetch
```

This will show you how your script gets broken into beats without fetching B-roll footage.