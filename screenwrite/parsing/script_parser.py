"""
Script parser for converting markdown video scripts into Beat objects.

The ScriptParser handles parsing markdown files into structured beats with
auto-generated search queries for B-roll asset fetching.

Markdown Script Specification:
- Metadata (key: value) at the top provides title, hook, channel
- Headers (# and ##) provide context for content sections
- Body text is automatically chunked into 5-10 second beats
- Inline B-roll instructions ([@action: content]) override auto-generated queries
- Each beat gets auto-generated stock keywords and YouTube search phrases
- Text is processed using a 2.5 words per second heuristic for timing
"""

import re
import logging
import os
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from dataclasses import dataclass
from ..core.beat import Beat
from ..config import (
    TARGET_MIN_DURATION,
    TARGET_MAX_DURATION,
    WORDS_PER_SECOND,
    SUPPORTED_ENCODINGS,
    BEAT_TEXT_TRUNCATION_LENGTH,
    STOCK_KEYWORD_STOP_WORDS,
    VISUAL_PATTERNS,
    YOUTUBE_PHRASE_STOP_WORDS,
    TECHNICAL_PATTERNS,
)
from ..utils.error_handling import (
    validate_markdown_file,
    InputValidationError,
    log_error_with_context
)
from ..utils.cache import load_cached_beats, cache_beats

logger = logging.getLogger(__name__)


@dataclass
class BRollInstruction:
    """Represents an inline B-roll instruction like [Show: ...]"""
    action: str  # "Show", "Display", "Annotation", etc.
    content: str  # The subject/content to display
    
    def to_query(self) -> str:
        """Convert instruction to a search query."""
        return self.content


@dataclass
class ScriptMetadata:
    """Metadata extracted from script header."""
    title: Optional[str] = None
    hook: Optional[str] = None
    channel: Optional[str] = None
    duration: Optional[str] = None
    thumbnail: Optional[str] = None
    tags: Optional[List[str]] = None
    
    def to_context_string(self) -> str:
        """Convert metadata to context for B-roll generation."""
        parts = []
        if self.title:
            parts.append(self.title)
        if self.channel:
            parts.append(self.channel)
        if self.tags:
            parts.extend(self.tags)
        return ' '.join(parts)


class ScriptParser:
    """
    Parser for converting markdown video scripts into Beat objects.
    
    The parser reads markdown files, extracts contextual information from headers,
    and chunks body text into logical beats with auto-generated search queries.
    """
    
    def __init__(self):
        """Initialize the script parser."""
        self.target_min_duration = TARGET_MIN_DURATION
        self.target_max_duration = TARGET_MAX_DURATION
        self.words_per_second = WORDS_PER_SECOND
    
    def parse(self, file_path: str, use_cache: bool = True) -> List[Beat]:
        """
        Parse a markdown script file into Beat objects.
        
        Args:
            file_path: Path to the markdown script file
            use_cache: Whether to use cached beats if available (default: True)
            
        Returns:
            List of Beat objects with auto-generated metadata
            
        Raises:
            InputValidationError: If the script file is invalid or cannot be processed
        """
        # Check cache first if enabled
        if use_cache and os.getenv('screenwrite_CACHE_BEATS'):
            cached_beats = load_cached_beats(file_path)
            if cached_beats:
                logger.info(f"Loaded {len(cached_beats)} beats from cache")
                return cached_beats
        
        # Validate input file using comprehensive validation
        validation_result = validate_markdown_file(file_path)
        
        if not validation_result.is_valid:
            log_error_with_context(
                logger, logging.ERROR,
                "Script validation failed",
                component="ScriptParser",
                file_path=file_path,
                error_message=validation_result.error_message
            )
            raise InputValidationError(validation_result.error_message)
        
        # Log any warnings from validation
        for warning in validation_result.warnings:
            logger.warning(f"Script validation warning: {warning}")
        
        try:
            # Read file content with proper error handling
            script_path = Path(file_path)
            
            # Try UTF-8 first, then fallback encodings
            content = None
            
            for encoding in SUPPORTED_ENCODINGS:
                try:
                    with open(script_path, 'r', encoding=encoding) as f:
                        content = f.read().strip()
                    if encoding != 'utf-8':
                        logger.info(f"Successfully read file using {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
            
            if content is None:
                raise InputValidationError(f"Cannot decode file content: {file_path}")
            
            if not content:
                raise InputValidationError(f"Script file is empty: {file_path}")
            
            # Extract context from headers, body text, and metadata
            context, body_text, metadata = self._extract_content(content)
            
            if not body_text.strip():
                raise InputValidationError(f"No body text found in script: {file_path}")
            
            # Add metadata context to improve B-roll generation
            full_context = context
            if metadata.title:
                full_context = metadata.title + ' ' + full_context
            
            # Extract B-roll instructions from body text
            body_with_instructions = self._extract_broll_instructions(body_text)
            
            # Chunk text into beats
            text_chunks = self._chunk_text(body_text, full_context)
            
            if not text_chunks:
                raise InputValidationError(f"No valid text chunks generated from script: {file_path}")
            
            # Generate Beat objects
            beats = []
            for i, chunk in enumerate(text_chunks):
                try:
                    beat_id = f"beat_{i+1:03d}"
                    
                    # Check if this chunk has an associated B-roll instruction
                    broll_instruction = self._find_associated_broll(chunk, body_with_instructions)
                    
                    visual_type = 'auto'
                    visual_content = None
                    
                    if broll_instruction:
                        # Use B-roll instruction as the primary query
                        stock_keyword = broll_instruction.content
                        youtube_phrase = broll_instruction.content
                        
                        # Map action to visual_type
                        action_lower = broll_instruction.action.lower()
                        if action_lower in ('annotation', 'text', 'title'):
                            visual_type = 'annotation'
                        elif action_lower in ('citation', 'source', 'credit'):
                            visual_type = 'citation'
                        elif action_lower in ('image', 'img', 'screenshot'):
                            visual_type = 'image'
                        else:
                            # Default for Show, Display, B-roll, etc.
                            visual_type = 'b-roll'
                            
                        visual_content = broll_instruction.content
                        
                        # Strip wrapping quotes from visual_content if present
                        if visual_content and len(visual_content) >= 2:
                            if (visual_content.startswith('"') and visual_content.endswith('"')) or \
                               (visual_content.startswith("'") and visual_content.endswith("'")):
                                visual_content = visual_content[1:-1].strip()
                    else:
                        # Auto-generate queries
                        stock_keyword = self._generate_stock_keyword(chunk, full_context)
                        youtube_phrase = self._generate_youtube_phrase(chunk, full_context)
                    
                    # Strip all [@...] tags from the displayed text to keep the script clean
                    # Use a regex that matches the same pattern as _extract_broll_instructions
                    clean_text = re.sub(r'\[\s*@([A-Z][a-zA-Z]*):\s*([^\]]+)\]', '', chunk).strip()
                    
                    # Fallback: if stripping left us with empty text (instruction-only beat),
                    # use the visual content as text so duration is > 0 and validation passes
                    if not clean_text and visual_content:
                        clean_text = visual_content
                    
                    # Ultimate fallback for safety
                    if not clean_text:
                        clean_text = chunk.strip()
                    
                    beat = Beat(
                        id=beat_id,
                        text=clean_text,
                        stock_keyword=stock_keyword,
                        youtube_search_phrase=youtube_phrase,
                        visual_type=visual_type,
                        visual_content=visual_content
                    )
                    beats.append(beat)
                    
                except Exception as e:
                    log_error_with_context(
                        logger, logging.ERROR,
                        f"Failed to create beat {i+1}",
                        component="ScriptParser",
                        chunk_text=chunk[:100] + "..." if len(chunk) > 100 else chunk,
                        error=e
                    )
                    # Continue processing other beats
                    continue
            
            if not beats:
                raise InputValidationError(f"No valid beats could be generated from script: {file_path}")
            
            # Log successful parsing summary
            total_duration = sum(beat.duration for beat in beats)
            logger.info(
                f"Successfully parsed script: {len(beats)} beats, "
                f"{total_duration:.1f}s total duration"
            )
            
            # Cache beats if caching is enabled
            if os.getenv('screenwrite_CACHE_BEATS'):
                cache_beats(file_path, beats)
                logger.debug(f"Cached {len(beats)} beats for {file_path}")
            
            return beats
            
        except InputValidationError:
            # Re-raise validation errors as-is
            raise
        except Exception as e:
            log_error_with_context(
                logger, logging.ERROR,
                "Unexpected error during script parsing",
                component="ScriptParser",
                file_path=file_path,
                error=e
            )
            raise InputValidationError(f"Failed to parse script file: {e}")
    
    
    def _extract_content(self, content: str) -> Tuple[str, str, ScriptMetadata]:
        """
        Extract metadata, context from headers, and body text from markdown content.
        
        Args:
            content: Raw markdown content
            
        Returns:
            Tuple of (context_from_headers, body_text, metadata)
        """
        lines = content.split('\n')
        headers = []
        body_lines = []
        metadata = ScriptMetadata()
        in_metadata = True
        
        for line in lines:
            original_line = line
            line = line.strip()
            
            if not line:
                # Blank line might signal end of metadata
                if in_metadata and body_lines:
                    in_metadata = False
                continue
            
            # Extract metadata (key: value format) at start of file
            if in_metadata and ':' in line and not line.startswith('#') and not line.startswith('['):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip().lower()
                    value = parts[1].strip()
                    
                    is_metadata = True
                    if key == 'title':
                        metadata.title = value
                    elif key == 'hook':
                        metadata.hook = value
                    elif key == 'channel':
                        metadata.channel = value
                    elif key == 'duration':
                        metadata.duration = value
                    elif key == 'thumbnail':
                        metadata.thumbnail = value
                    elif key == 'tags':
                        metadata.tags = [t.strip() for t in value.split(',')]
                    else:
                        is_metadata = False
                    
                    if is_metadata:
                        continue  # Skip metadata lines from body
            
            in_metadata = False  # Stop looking for metadata after first non-metadata line
            
            # Extract headers for context
            if line.startswith('#'):
                # Remove markdown header syntax and add to context
                header_text = re.sub(r'^#+\s*', '', line).strip()
                if header_text:
                    headers.append(header_text)
            else:
                # Add non-header content to body
                body_lines.append(line)
        
        context = ' '.join(headers) if headers else ''
        body_text = ' '.join(body_lines)
        
        return context, body_text, metadata
    
    def _chunk_text(self, text: str, context: str = '') -> List[str]:
        """
        Chunk text into segments targeting 5-10 second beats.
        
        Args:
            text: Body text to chunk
            context: Context from headers to inform chunking
            
        Returns:
            List of text chunks, each targeting 5-10 seconds
        """
        # Calculate target word counts for duration bounds
        # Use ceiling to ensure we meet the minimum duration requirement
        import math
        min_words = math.ceil(self.target_min_duration * self.words_per_second)  # 13 words for 5+ seconds
        max_words = int(self.target_max_duration * self.words_per_second)  # 25 words
        target_words = int((self.target_min_duration + self.target_max_duration) / 2 * self.words_per_second)  # ~19 words
        
        # Split text into sentences for natural chunking
        sentences = self._split_into_sentences(text)
        
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            
            # If adding this sentence would exceed max words, finalize current chunk
            if current_word_count > 0 and current_word_count + sentence_words > max_words:
                # Only finalize if we have at least minimum words
                if current_word_count >= min_words:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = [sentence]
                    current_word_count = sentence_words
                else:
                    # Current chunk is too small, add sentence anyway to avoid creating invalid beats
                    current_chunk.append(sentence)
                    current_word_count += sentence_words
            else:
                # Add sentence to current chunk
                current_chunk.append(sentence)
                current_word_count += sentence_words
                
                # If we've reached target words, consider finalizing
                if current_word_count >= target_words:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
                    current_word_count = 0
        
        # Handle remaining text
        if current_chunk:
            remaining_text = ' '.join(current_chunk)
            remaining_words = len(remaining_text.split())
            
            # If the last chunk is too small, merge with previous chunk
            if remaining_words < min_words and chunks:
                chunks[-1] = chunks[-1] + ' ' + remaining_text
            else:
                chunks.append(remaining_text)
        
        # Post-process to ensure all chunks meet minimum requirements
        final_chunks = []
        for chunk in chunks:
            chunk_words = len(chunk.split())
            if chunk_words < min_words:
                # Merge with previous chunk if possible
                if final_chunks:
                    final_chunks[-1] = final_chunks[-1] + ' ' + chunk
                else:
                    # This is the first chunk and it's too small - keep it anyway
                    final_chunks.append(chunk)
            elif chunk_words > max_words:
                # Split chunks that are too long
                split_chunks = self._split_long_chunk(chunk, min_words, max_words)
                final_chunks.extend(split_chunks)
            else:
                final_chunks.append(chunk)
        
        # Handle edge case where text is too short for even one valid beat
        if not final_chunks and text.strip():
            final_chunks = [text.strip()]
        
        return final_chunks
    
    def _split_long_chunk(self, chunk: str, min_words: int, max_words: int) -> List[str]:
        """
        Split a chunk that's too long into smaller valid chunks.
        
        Args:
            chunk: Text chunk that's too long
            min_words: Minimum words per chunk
            max_words: Maximum words per chunk
            
        Returns:
            List of smaller chunks
        """
        words: List[str] = chunk.split()
        chunks: List[str] = []
        
        # Split into chunks of target size
        target_size: int = (min_words + max_words) // 2  # ~19 words
        
        i: int = 0
        while i < len(words):
            remaining_total = len(words) - i
            
            # If what's left already fits in one chunk, take it all
            if remaining_total <= max_words:
                chunks.append(' '.join(words[i:]))
                break
                
            # We must split. Determine how much to take.
            # We want to take roughly target_size, but we must leave at least min_words.
            # So chunk_size <= remaining_total - min_words
            chunk_size = min(target_size, remaining_total - min_words)
            
            # Also ensure chunk_size itself is at least min_words
            chunk_size = max(min_words, chunk_size)
            
            # Safety check: if chunk_size > max_words here, it means we can't 
            # satisfy both min and max requirements (e.g. max < 2*min).
            # In that case, we prioritize max_words to avoid huge beats.
            chunk_size = min(chunk_size, max_words)
            
            chunk_words: List[str] = words[i:i + chunk_size]
            chunks.append(' '.join(chunk_words))
            i += chunk_size
        
        return chunks
    
    def _extract_broll_instructions(self, text: str) -> Dict[str, List[BRollInstruction]]:
        """
        Extract all B-roll instructions from text.
        
        Finds patterns like [@Show: content], [@Display: content], etc.
        
        Args:
            text: Text to search for instructions
            
        Returns:
            Dictionary mapping instruction content to list of BRollInstruction objects
        """
        instructions_dict = {}
        
        # Pattern: [@action: content] where action is capitalized
        # Matches [@Show: ...], [@Display: ...], [@Annotation: ...], etc.
        # Supports optional space: [ @Show: ...]
        pattern = r'\[\s*@([A-Z][a-zA-Z]*):\s*([^\]]+)\]'
        
        matches = re.finditer(pattern, text)
        
        for match in matches:
            action = match.group(1)
            content = match.group(2).strip()
            
            instruction = BRollInstruction(action=action, content=content)
            
            # Store by content for easy lookup
            if content not in instructions_dict:
                instructions_dict[content] = []
            instructions_dict[content].append(instruction)
        
        return instructions_dict
    
    def _find_associated_broll(self, chunk: str, instructions_dict: Dict[str, List[BRollInstruction]]) -> Optional[BRollInstruction]:
        """
        Find if a text chunk has an associated B-roll instruction.
        
        Looks for instructions that appear near the chunk text (before or within).
        
        Args:
            chunk: Text chunk to check
            instructions_dict: Dictionary of extracted instructions (content -> list of BRollInstructions)
            
        Returns:
            BRollInstruction object if found, None otherwise
        """
        if not instructions_dict:
            return None
        
        # Check if any instruction content appears in or near this chunk
        chunk_lower = chunk.lower()
        
        for content, instructions in instructions_dict.items():
            content_lower = content.lower()
            
            # Look for the instruction content in the chunk
            # This handles cases like "[Display: pages from Mastering Pac-Man...]" 
            # appearing just before the chunk text
            if content_lower in chunk_lower:
                # Return the first matching instruction
                return instructions[0]
        
        return None
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences for natural chunking boundaries.
        
        Args:
            text: Text to split
            
        Returns:
            List of sentences
        """
        # Simple sentence splitting on common punctuation
        # This handles most cases while being robust
        sentence_endings = r'[.!?]+\s+'
        sentences = re.split(sentence_endings, text)
        
        # Clean up and filter empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # If no sentence boundaries found, split on other punctuation or length
        if len(sentences) <= 1 and text.strip():
            # Try splitting on commas, semicolons, or colons
            alt_split = re.split(r'[,;:]\s+', text)
            if len(alt_split) > 1:
                sentences = [s.strip() for s in alt_split if s.strip()]
            else:
                # Fall back to word-based chunking for very long sentences
                words = text.split()
                if len(words) > 30:  # Arbitrary threshold for "too long"
                    # Split into smaller chunks of ~15 words each
                    chunk_size = 15
                    sentences = []
                    for i in range(0, len(words), chunk_size):
                        chunk = ' '.join(words[i:i + chunk_size])
                        sentences.append(chunk)
                else:
                    sentences = [text.strip()]
        
        return sentences
    
    def _generate_stock_keyword(self, text: str, context: str = '') -> str:
        """
        Generate a stock ScreenWrite keyword from beat text.
        
        Args:
            text: Beat text to analyze
            context: Additional context from headers
            
        Returns:
            Stock ScreenWrite search keyword
        """
        # Focus on the beat text primarily, use context as secondary
        full_text = f"{text} {context}".strip()
        
        # Extract key nouns and descriptive phrases
        # Remove common stop words and focus on visual elements
        stop_words = STOCK_KEYWORD_STOP_WORDS
        
        # Extract meaningful words
        words = re.findall(r'\b[a-zA-Z]+\b', full_text.lower())
        meaningful_words = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Look for visual/action keywords that work well for stock ScreenWrite
        visual_keywords = []
        
        # Common visual elements for stock ScreenWrite - prioritize beat-specific content
        # Keys are the strong search terms we want to use
        # Values are the trigger words found in text that map to these terms
        visual_patterns = VISUAL_PATTERNS
        
        # Find matching visual categories from beat text
        meaningful_words_set = set(meaningful_words)
        for category, triggers in visual_patterns.items():
            for trigger in triggers:
                if trigger in meaningful_words_set:
                    visual_keywords.append(category)
        
        # If we found visual keywords, use the most relevant ones
        if visual_keywords:
            # Remove duplicates while preserving order
            seen = set()
            unique_keywords = []
            for kw in visual_keywords:
                if kw not in seen:
                    seen.add(kw)
                    unique_keywords.append(kw)
            result = ' '.join(unique_keywords[:3])
        else:
            # Fall back to first few meaningful words from the beat text
            if meaningful_words:
                result = ' '.join(meaningful_words[:3])
            else:
                # Ultimate fallback
                result = 'person working computer'
        
        return result
    
    def _generate_youtube_phrase(self, text: str, context: str = '') -> str:
        """
        Generate a YouTube search phrase from beat text.
        
        Args:
            text: Beat text to analyze
            context: Additional context from headers
            
        Returns:
            YouTube search phrase
        """
        # Focus on beat text primarily for specific content
        full_text = f"{text} {context}".strip()
        
        # Extract key phrases and technical terms
        # YouTube searches work better with specific phrases and technical terms
        
        # Look for specific technical terms, product names, actions
        key_terms = []
        
        # Extract important nouns, verbs, and technical terms from beat text
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())  # Focus on beat text
        
        # Filter for meaningful terms (longer words, technical terms, actions)
        stop_words = YOUTUBE_PHRASE_STOP_WORDS
        
        meaningful_terms = []
        for word in words:
            if len(word) > 3 and word not in stop_words:
                meaningful_terms.append(word)
        
        # Look for specific technical patterns in the beat text
        technical_patterns = TECHNICAL_PATTERNS
        
        for pattern in technical_patterns:
            matches = re.findall(pattern, text)
            key_terms.extend([m.lower() for m in matches])
        
        # Combine meaningful terms and technical patterns
        all_terms = meaningful_terms + key_terms
        
        # Remove duplicates while preserving order
        seen = set()
        unique_terms = []
        for term in all_terms:
            term_lower = term.lower()
            if term_lower not in seen:
                seen.add(term_lower)
                unique_terms.append(term)
        
        # Build search phrase - take most relevant terms
        if unique_terms:
            # Take first 3-4 most relevant terms from the beat
            result = ' '.join(unique_terms[:4])
        else:
            # Fallback to any words from beat text
            beat_words = text.split()
            filtered_words = [w for w in beat_words if len(w) > 3]
            if filtered_words:
                result = ' '.join(filtered_words[:4])
            else:
                result = 'programming tutorial'
        
        return result
