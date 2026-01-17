"""
Script parser for converting markdown video scripts into Beat objects.

The ScriptParser handles parsing markdown files into structured beats with
auto-generated search queries for B-roll asset fetching.

Markdown Script Specification:
- Headers (# and ##) provide context for content sections
- Body text is automatically chunked into 5-10 second beats
- Each beat gets auto-generated stock keywords and YouTube search phrases
- Text is processed using a 2.5 words per second heuristic for timing
"""

import re
import logging
from pathlib import Path
from typing import List, Optional, Tuple
from ..core.beat import Beat
from ..utils.error_handling import (
    validate_markdown_file,
    InputValidationError,
    log_error_with_context
)

logger = logging.getLogger(__name__)


class ScriptParser:
    """
    Parser for converting markdown video scripts into Beat objects.
    
    The parser reads markdown files, extracts contextual information from headers,
    and chunks body text into logical beats with auto-generated search queries.
    """
    
    def __init__(self):
        """Initialize the script parser."""
        self.target_min_duration = 5.0  # Minimum beat duration in seconds
        self.target_max_duration = 10.0  # Maximum beat duration in seconds
        self.words_per_second = 2.5  # Heuristic for duration calculation
    
    def parse(self, file_path: str) -> List[Beat]:
        """
        Parse a markdown script file into Beat objects.
        
        Args:
            file_path: Path to the markdown script file
            
        Returns:
            List of Beat objects with auto-generated metadata
            
        Raises:
            InputValidationError: If the script file is invalid or cannot be processed
        """
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
            encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
            
            for encoding in encodings:
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
            
            # Extract context from headers and body text
            context, body_text = self._extract_content(content)
            
            if not body_text.strip():
                raise InputValidationError(f"No body text found in script: {file_path}")
            
            # Chunk text into beats
            text_chunks = self._chunk_text(body_text, context)
            
            if not text_chunks:
                raise InputValidationError(f"No valid text chunks generated from script: {file_path}")
            
            # Generate Beat objects
            beats = []
            for i, chunk in enumerate(text_chunks):
                try:
                    beat_id = f"beat_{i+1:03d}"
                    stock_keyword = self._generate_stock_keyword(chunk, context)
                    youtube_phrase = self._generate_youtube_phrase(chunk, context)
                    
                    beat = Beat(
                        id=beat_id,
                        text=chunk.strip(),
                        stock_keyword=stock_keyword,
                        youtube_search_phrase=youtube_phrase
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
    
    
    def _extract_content(self, content: str) -> Tuple[str, str]:
        """
        Extract context from headers and body text from markdown content.
        
        Args:
            content: Raw markdown content
            
        Returns:
            Tuple of (context_from_headers, body_text)
        """
        lines = content.split('\n')
        headers = []
        body_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
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
        
        return context, body_text
    
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
        words = chunk.split()
        chunks = []
        
        # Split into chunks of target size
        target_size = (min_words + max_words) // 2  # ~19 words
        
        i = 0
        while i < len(words):
            # Take target_size words, but don't exceed max_words
            chunk_size = min(target_size, max_words, len(words) - i)
            
            # If this would leave a remainder that's too small, adjust
            remaining = len(words) - i - chunk_size
            if remaining > 0 and remaining < min_words:
                # Reduce current chunk size to leave enough for next chunk
                chunk_size = max(min_words, len(words) - i - min_words)
            
            chunk_words = words[i:i + chunk_size]
            chunks.append(' '.join(chunk_words))
            i += chunk_size
        
        return chunks
    
    def _generate_stock_keyword(self, text: str, context: str = '') -> str:
        """
        Generate a stock footage keyword from beat text.
        
        Args:
            text: Beat text to analyze
            context: Additional context from headers
            
        Returns:
            Stock footage search keyword
        """
        # Focus on the beat text primarily, use context as secondary
        full_text = f"{text} {context}".strip()
        
        # Extract key nouns and descriptive phrases
        # Remove common stop words and focus on visual elements
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
            'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
            'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them',
            'your', 'first', 'then', 'now', 'here', 'there', 'when', 'where', 'how'
        }
        
        # Extract meaningful words
        words = re.findall(r'\b[a-zA-Z]+\b', full_text.lower())
        meaningful_words = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Look for visual/action keywords that work well for stock footage
        visual_keywords = []
        
        # Common visual elements for stock footage - prioritize beat-specific content
        visual_patterns = {
            'coding': ['coding', 'programming', 'developer', 'programmer', 'code'],
            'computer': ['computer', 'laptop', 'keyboard', 'screen', 'monitor', 'typing'],
            'learning': ['tutorial', 'learning', 'education', 'student', 'study'],
            'business': ['office', 'meeting', 'presentation', 'team', 'work', 'business'],
            'writing': ['writing', 'editor', 'file', 'document', 'text'],
            'terminal': ['terminal', 'command', 'console', 'shell'],
            'person': ['person', 'people', 'man', 'woman', 'user'],
            'technology': ['software', 'application', 'program', 'system', 'digital']
        }
        
        # Find matching visual categories from beat text
        for category, keywords in visual_patterns.items():
            for keyword in keywords:
                if keyword in meaningful_words:
                    visual_keywords.append(keyword)
        
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
        stop_words = {
            'this', 'that', 'with', 'from', 'they', 'have', 'will', 'been',
            'were', 'said', 'each', 'which', 'their', 'time', 'would', 'then',
            'first', 'need', 'your', 'like', 'using', 'called', 'example'
        }
        
        meaningful_terms = []
        for word in words:
            if len(word) > 3 and word not in stop_words:
                meaningful_terms.append(word)
        
        # Look for specific technical patterns in the beat text
        technical_patterns = [
            r'\b[A-Z][a-zA-Z]*\s+[A-Z][a-zA-Z]*\b',  # Product names (e.g., "Visual Studio")
            r'\b\w+\.py\b',  # File names
            r'\b\w+ing\b',  # Actions (e.g., "programming", "coding")
        ]
        
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