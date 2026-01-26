# Markdown Cheat Sheet

Quick reference for the **ScreenWrite** script format.

## Metadata (Top of File)
```markdown
Title: Your Video Title
Hook: Opening hook that grabs attention
Tags: tag1, tag2, tag3
```

## Headers (Organization)
```markdown
# Topic Name (Main context)
## Section Name (Segment context)
```

## Visual Instructions
Place these immediately before the text they accompany.

```markdown
[B-roll: video footage, interviews, or gameplay]
[Image: images, screenshots, diagrams, or UI]
[Annotation: prominent on-screen text or labels]
[Citation: source attribution (bottom left corner)]
```

---

## Common Patterns

### Multi-Instruction Section
```markdown
## Historical Context

[Annotation: "Year: 1985"]
This happened in 1985 and it was important.

[Image: historical photograph]
Here is what it looked like.

[Citation: Wikipedia]
Documentation of this moment.
```

---

## Do's and Don'ts

### ✅ DO
- **Be Specific**: `[Image: Python code in VS Code]`
- **Chain Logically**: Place instructions in the order they should appear.
- **Add Citations**: Credit your sources clearly.

### ❌ DON'T
- **Be Vague**: Avoid `[Image: stuff]` or `[B-roll: things]`.
- **Use Wrong Syntax**: Brackets and Colons are required: `[Action: Description]`.
- **Over-instruct**: Let the text drive the timing; use instructions for specific needs.

---

## Word Count Guide
Target **13-25 words** per beat for optimal 5-10 second pacing.

- **Too short**: "Open the terminal." (3 words)
- **Good**: "Open your terminal and navigate to your Documents folder using the cd command." (14 words)
- **Too long**: Break complex sentences into two distinct beats.

---

## Testing
Verify your script structure with the CLI:

```bash
screenwrite your_script.md --no-fetch --verbose
```