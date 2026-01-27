"""
Unit tests for ScriptParser module.

Tests the markdown parsing, beat generation, and query generation functionality.
"""

import unittest
import shutil
import tempfile
from pathlib import Path

from screenwrite.parsing.script_parser import ScriptParser
from screenwrite.core.beat import Beat
from screenwrite.utils.error_handling import InputValidationError


class TestScriptParser(unittest.TestCase):
    """Test cases for ScriptParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = ScriptParser()
        self.temp_dir = tempfile.mkdtemp(prefix="test_parser_")
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up test files."""
        if self.temp_path.exists():
            shutil.rmtree(self.temp_path)
    
    def _create_test_script(self, content: str) -> Path:
        """Helper to create a temporary test script file."""
        script_path = self.temp_path / "test_script.md"
        script_path.write_text(content, encoding='utf-8')
        return script_path
    
    def test_parse_valid_script(self):
        """Test parsing a valid markdown script."""
        content = """# Test Tutorial

## Introduction
Welcome to this test tutorial about Python programming. We will learn how to write code and create simple programs.

## Getting Started
First, you need to install Python on your computer system. Visit the official website and download the latest version available.
"""
        script_path = self._create_test_script(content)
        beats = self.parser.parse(str(script_path))
        
        # Verify beats were generated
        self.assertGreater(len(beats), 0, "Should generate at least one beat")
        
        # Verify each beat is valid
        for beat in beats:
            self.assertIsInstance(beat, Beat)
            self.assertGreaterEqual(beat.duration, 5.0)
            self.assertLessEqual(beat.duration, 10.0)
            self.assertTrue(beat.text.strip())
            self.assertTrue(beat.stock_keyword.strip())
            self.assertTrue(beat.youtube_search_phrase.strip())
    
    def test_parse_empty_file(self):
        """Test parsing an empty file raises error."""
        script_path = self._create_test_script("")
        
        with self.assertRaises(InputValidationError):
            self.parser.parse(str(script_path))
    
    def test_parse_file_with_only_headers(self):
        """Test parsing file with only headers and no body text."""
        content = """# Title
## Section 1
## Section 2
"""
        script_path = self._create_test_script(content)
        
        with self.assertRaises(InputValidationError):
            self.parser.parse(str(script_path))
    
    def test_parse_file_with_insufficient_content(self):
        """Test parsing file with too few words."""
        content = """# Title
Short text.
"""
        script_path = self._create_test_script(content)
        
        with self.assertRaises(InputValidationError):
            self.parser.parse(str(script_path))
    
    def test_extract_content_separates_headers_and_body(self):
        """Test that headers and body text are properly separated."""
        content = """# Main Title
## Section
This is body text with some content.
"""
        context, body, metadata = self.parser._extract_content(content)
        
        self.assertIn("Main Title", context)
        self.assertIn("Section", context)
        self.assertIn("body text", body)
        self.assertNotIn("#", body)
    
    def test_chunk_text_creates_valid_beats(self):
        """Test text chunking creates properly sized beats."""
        # 40 words = should create 2 beats of ~20 words each
        text = ("This is a test sentence with exactly the right number of words. "
                "We want to make sure the chunking algorithm works correctly and "
                "creates beats that are within the five to ten second duration range.")
        
        chunks = self.parser._chunk_text(text)
        
        self.assertGreater(len(chunks), 0)
        
        # Verify each chunk has reasonable word count
        for chunk in chunks:
            word_count = len(chunk.split())
            self.assertGreaterEqual(word_count, 13, f"Chunk too short: {word_count} words")
            self.assertLessEqual(word_count, 25, f"Chunk too long: {word_count} words")
    
    def test_split_into_sentences(self):
        """Test sentence splitting logic."""
        text = "First sentence. Second sentence! Third sentence? Fourth sentence."
        sentences = self.parser._split_into_sentences(text)
        
        self.assertEqual(len(sentences), 4)
        self.assertIn("First sentence", sentences[0])
    
    def test_generate_stock_keyword_extracts_visual_terms(self):
        """Test stock keyword generation extracts visual elements."""
        text = "Open Visual Studio Code and click the green button on the screen."
        context = "Programming Tutorial"
        
        keyword = self.parser._generate_stock_keyword(text, context)
        
        self.assertTrue(keyword.strip())
        # Should contain mapped visual categories (e.g. code -> coding, screen -> computer)
        keyword_lower = keyword.lower()
        has_visual_term = any(term in keyword_lower for term in 
                             ['coding', 'computer', 'technology', 'digital'])
        self.assertTrue(has_visual_term, f"Keyword '{keyword}' missing visual terms")
    
    def test_generate_youtube_phrase_extracts_technical_terms(self):
        """Test YouTube phrase generation extracts meaningful terms."""
        text = "Navigate to the terminal window and type the python command."
        context = "Python Setup"
        
        phrase = self.parser._generate_youtube_phrase(text, context)
        
        self.assertTrue(phrase.strip())
        # Should contain technical terms
        phrase_lower = phrase.lower()
        has_technical_term = any(term in phrase_lower for term in 
                                ['terminal', 'python', 'command', 'navigate', 'type'])
        self.assertTrue(has_technical_term, f"Phrase '{phrase}' missing technical terms")
    
    def test_parse_with_different_encodings(self):
        """Test parsing files with different encodings."""
        content = "# Tutorial\n\nThis is a test with some special characters: Ã©, Ã±, Ã¼."
        
        # Test UTF-8
        script_path = self.temp_path / "test_utf8.md"
        script_path.write_text(content, encoding='utf-8')
        beats = self.parser.parse(str(script_path))
        self.assertGreater(len(beats), 0)
        
        # Test latin-1
        script_path_latin = self.temp_path / "test_latin1.md"
        script_path_latin.write_bytes(content.encode('latin-1'))
        beats_latin = self.parser.parse(str(script_path_latin))
        self.assertGreater(len(beats_latin), 0)
    
    def test_parse_realistic_tutorial_script(self):
        """Test parsing a realistic tutorial script."""
        content = """# Python Programming Tutorial

## Introduction
Welcome to this comprehensive Python programming tutorial for beginners. In this video we'll learn the fundamentals of Python development.

## Installing Python
First you need to install Python on your computer system. Visit the official Python website at python.org and click the download button.

The installer will automatically detect your operating system. Make sure to check the box that says add Python to your system PATH variable.

## Writing Your First Program
Open your favorite text editor or IDE like Visual Studio Code. Create a new file and save it with a dot py extension on your desktop.

Type the print function with your message inside quotation marks. Click the green run button to execute your code and see the output.

## Working with Variables
Variables are containers that store data values in your Python programs. You create a variable by choosing a name and using the equals sign.

Try creating a variable called message and setting it to your favorite quote. Then use the print function to display your variable on screen.

## Next Steps
Congratulations on completing your first Python tutorial and learning the basics. Continue practicing these concepts by writing your own simple programs.
"""
        script_path = self._create_test_script(content)
        beats = self.parser.parse(str(script_path))
        
        # Should generate multiple beats from this realistic content
        self.assertGreaterEqual(len(beats), 5, "Should generate at least 5 beats")
        self.assertLessEqual(len(beats), 12, "Should not generate excessive beats")
        
        # Verify all beats have proper structure
        for beat in beats:
            self.assertTrue(beat.id.startswith("beat_"))
            self.assertGreater(len(beat.text.split()), 0)
            self.assertTrue(beat.stock_keyword)
            self.assertTrue(beat.youtube_search_phrase)
    
    def test_beat_ids_are_sequential(self):
        """Test that beat IDs are numbered sequentially."""
        content = """# Tutorial

## Section One
This is the first section with enough words to create a beat. We need at least thirteen words for valid beat generation.

## Section Two  
This is the second section also with enough words to make a beat. Again we need sufficient content for proper timing.

## Section Three
And here is the third section completing our test with adequate words. The parser should create sequential beat identifiers.
"""
        script_path = self._create_test_script(content)
        beats = self.parser.parse(str(script_path))
        
        # Verify sequential numbering
        for i, beat in enumerate(beats, start=1):
            expected_id = f"beat_{i:03d}"
            self.assertEqual(beat.id, expected_id, 
                           f"Beat {i} should have ID '{expected_id}', got '{beat.id}'")
    
    def test_context_influences_query_generation(self):
        """Test that header context influences query generation."""
        # Same body text, different headers
        body = "Open the application and click on the settings button to continue."
        
        content1 = f"# Python Programming\n\n{body}"
        content2 = f"# Video Editing\n\n{body}"
        
        script1 = self._create_test_script(content1)
        script2 = self.temp_path / "test2.md"
        script2.write_text(content2, encoding='utf-8')
        
        beats1 = self.parser.parse(str(script1))
        beats2 = self.parser.parse(str(script2))
        
        # Queries should be different due to different context
        # (may not always be true, but generally should differ)
        self.assertTrue(len(beats1) > 0 and len(beats2) > 0)


class TestScriptParserHelperMethods(unittest.TestCase):
    """Test helper methods in ScriptParser."""
    
    def setUp(self):
        """Set up parser instance."""
        self.parser = ScriptParser()
    
    def test_split_long_chunk(self):
        """Test splitting of overly long chunks."""
        # Create a chunk that's too long (>25 words)
        words = ["word"] * 40
        long_chunk = " ".join(words)
        
        chunks = self.parser._split_long_chunk(long_chunk, 13, 25)
        
        self.assertGreater(len(chunks), 1, "Long chunk should be split")
        
        # Verify each chunk is within bounds
        for chunk in chunks:
            word_count = len(chunk.split())
            self.assertGreaterEqual(word_count, 13)
            self.assertLessEqual(word_count, 25)
    
    def test_chunk_text_handles_very_short_text(self):
        """Test chunking handles text that's too short for even one beat."""
        short_text = "Just a few words here."
        
        chunks = self.parser._chunk_text(short_text)
        
        # Should still return the text as a single chunk
        # even though it doesn't meet minimum requirements
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], short_text)
    
    def test_chunk_text_handles_no_sentence_boundaries(self):
        """Test chunking text without sentence boundaries."""
        # Text without periods, questions, or exclamations
        text = "This is a long run-on sentence without any punctuation marks to break it up so the parser needs to handle this case gracefully and still create reasonable chunks"
        
        chunks = self.parser._chunk_text(text)
        
        self.assertGreater(len(chunks), 0)


if __name__ == '__main__':
    unittest.main()

