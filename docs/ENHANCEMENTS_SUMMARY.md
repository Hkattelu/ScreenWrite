# Markdown Format Enhancements Summary

## Overview

The markdown flavor has been significantly enhanced to support more robust video scripts with better B-roll control, metadata, and structure.

## What Was Added

### 1. **Metadata Support**

Scripts can now begin with structured metadata:

```markdown
Title: Video Title
Hook: Opening statement
Channel: Channel Name
Duration: 12:30
Tags: tag1, tag2, tag3
```

**Benefits:**
- Provides clear context for B-roll generation
- Improves search query relevance
- Documents video structure upfront
- Supports programmatic processing

### 2. **Inline B-Roll Instructions**

Explicitly specify what footage/images to show using `[action: content]`:

```markdown
[Show: something specific]
[Display: overlay content]
[Annotation: on-screen text]
[Screenshot: UI interface]
[B-roll: video footage]
[Footage: specific recording]
[Interview: interview clip]
[Visual: general visual reference]
```

**Benefits:**
- Override auto-generated search queries
- Precise control over B-roll selection
- Self-documenting video script
- Reduces reliance on keyword guessing

### 3. **Enhanced Text Organization**

Better support for structured sections:

```markdown
## Motivation
## Actual Title Options
## Hook
## Content
  ### Section 1
  ### Section 2
## Call to Action
## Sources / References
```

**Benefits:**
- Aligns with video production conventions
- Makes scripts more readable
- Better organization for complex videos
- Supports future analytics/metadata extraction

### 4. **Link and Reference Support**

Include sources and external references:

```markdown
## Sources

- [Link Title](URL) - Description
- [Another Link](URL) - More details
```

**Benefits:**
- Cite sources properly
- Generate descriptions for video
- Track research and references
- Enable proper attribution

## Files Added/Modified

### New Documentation

- **`docs/MARKDOWN_SCRIPT_FORMAT.md`** - Complete specification of enhanced format
- **`docs/UPGRADE_TO_ENHANCED_FORMAT.md`** - Migration guide for existing scripts
- **`docs/ENHANCEMENTS_SUMMARY.md`** - This file

### Updated Documentation

- **`docs/MARKDOWN_SCRIPT_GUIDE.md`** - Added reference to new enhanced format

### Enhanced Code

- **`vid_orchestrator/parsing/script_parser.py`** - Updated to support:
  - Metadata extraction (`ScriptMetadata` class)
  - B-roll instruction parsing (`BRollInstruction` class)
  - Instruction detection and association
  - Better context generation for queries

### Example Files

- **`examples/video_walkthroughs_enhanced.md`** - Full example using the enhanced format
  - Your walkthrough script converted to new format
  - Shows all features in use
  - 600+ lines of properly formatted content

## Backwards Compatibility

✅ **Fully backwards compatible**

Old scripts continue to work:
- Scripts without metadata parse fine
- Scripts without `[action: ...]` instructions work normally
- Plain headers and body text processed as before

You can upgrade gradually without breaking existing pipelines.

## How to Use Enhanced Format

### Minimal Upgrade (Recommended Starting Point)

```markdown
Title: Your Video Title

## Content

Your script content here...
```

### Medium Enhancement

```markdown
Title: Your Video Title
Hook: Opening statement

## Content

[Show: specific visual element]
Main content with explicit B-roll guidance...
```

### Full Enhancement

```markdown
Title: Your Video Title
Hook: Opening statement
Channel: Your Channel
Tags: relevant, tags, here

## Motivation
Why this video matters...

## Content

### Section 1
[Show: relevant footage]
Content...

### Section 2
[Display: related content]
More content...

## Call to Action
Final message...

## Sources
- References...
```

## Benefits

| Feature | Before | After |
|---------|--------|-------|
| **Metadata** | Implicit/contextual | Explicit structured data |
| **B-roll Control** | Auto-generated only | Manual override available |
| **Structure** | Loose hierarchy | Clear sections |
| **References** | Not tracked | Documented links |
| **Intent** | Inferred from text | Self-documenting |
| **Search Queries** | Keyword guessing | Explicit instructions |

## Migration Path

1. **Phase 1**: Add Title and Hook to existing scripts
2. **Phase 2**: Add `[Show: ...]` instructions where obvious
3. **Phase 3**: Reorganize into Content, Sections, CTA
4. **Phase 4**: Add Sources and complete documentation

Each phase is optional and backwards compatible.

## Examples

### Your Walkthrough Script

The full walkthrough script about game guides has been converted to the enhanced format:

**File:** `examples/video_walkthroughs_enhanced.md`

Shows:
- Complete metadata header
- All nine section types
- Strategic use of B-roll instructions
- Proper linking of sources
- Professional structure

**Key sections:**
- Motivation explaining why this matters
- Multiple title options
- Hook to grab viewers
- Four content sections with detailed guidance
- Call to action
- Complete source citations

### Using as Template

Use this file as a template for your own scripts:

1. Copy the structure
2. Replace title/hook/content
3. Add your specific footage instructions
4. Include your sources
5. Parse with vid-orchestrator

## Parser Implementation

The `ScriptParser` now:

1. **Extracts metadata** from top of file (key: value pairs)
2. **Parses B-roll instructions** using regex pattern `[Action: content]`
3. **Associates instructions with beats** (future enhancement)
4. **Generates enhanced context** combining metadata + headers
5. **Allows instruction override** of auto-generated queries

### Regex Pattern

B-roll instructions are identified by:
```regex
\[([A-Z][a-z]+):\s*([^\]]+)\]
```

Matches:
- `[Show: ...]`
- `[Display: ...]`
- `[Annotation: ...]`
- `[Screenshot: ...]`
- `[B-roll: ...]`
- etc.

## Next Steps

### Short Term

- Test enhanced format with complex scripts
- Gather feedback on instruction syntax
- Refine regex pattern if needed

### Medium Term

- Improve instruction-to-beat association logic
- Add instruction position tracking
- Support grouped instructions

### Long Term

- Extract metadata to video metadata
- Generate segment descriptions from instructions
- Analytics on most-used instructions
- Custom instruction types

## Testing

To test the enhanced parser:

```bash
# Parse enhanced format script
python -m vid_orchestrator examples/video_walkthroughs_enhanced.md --output test.fcpxml --verbose

# Compare with non-enhanced version
python -m vid_orchestrator old_script.md --output old.fcpxml --verbose
```

Both should generate valid output (backwards compatibility).

## Reference

- **Format Spec**: `docs/MARKDOWN_SCRIPT_FORMAT.md`
- **Migration Guide**: `docs/UPGRADE_TO_ENHANCED_FORMAT.md`
- **Example Script**: `examples/video_walkthroughs_enhanced.md`
- **Parser Code**: `vid_orchestrator/parsing/script_parser.py`

## Questions & Feedback

The enhanced format is designed to be:
- **Intuitive** - Natural markdown syntax
- **Flexible** - Use as much or as little as needed
- **Powerful** - Explicit control when you need it
- **Compatible** - Works with existing scripts

See documentation files for detailed syntax, examples, and best practices.
