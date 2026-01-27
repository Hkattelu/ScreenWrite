"""
Unit tests for XMLGenerator module.

Tests FCPXML 1.8 generation, validation, and structure.
"""

import unittest
import shutil
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from screenwrite.generators.xml_generator import XMLGenerator
from screenwrite.core.beat import Beat


class TestXMLGenerator(unittest.TestCase):
    """Test cases for XMLGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = XMLGenerator(framerate=30)
        self.temp_dir = tempfile.mkdtemp(prefix="test_xml_")
        self.temp_path = Path(self.temp_dir)
        
        # Create test beats
        # Note: Beat class auto-calculates duration from text.
        # We need enough words to pass validation (3-10 seconds).
        # WORDS_PER_SECOND is 3. So 9-30 words.
        self.test_beats = [
            Beat(
                id="beat_001",
                text="This is a long enough beat text to satisfy the minimum duration requirement of three seconds.",
                stock_keyword="test coding",
                youtube_search_phrase="test programming tutorial"
            ),
            Beat(
                id="beat_002", 
                text="Another beat with enough words to ensure we are within the valid range for our unit tests here.",
                stock_keyword="computer programming",
                youtube_search_phrase="software development demo"
            )
        ]
        
        # Create mock asset files
        self.asset_map = {}
        for beat in self.test_beats:
            asset_path = self.temp_path / f"{beat.id}.mp4"
            asset_path.write_text("mock video content")
            self.asset_map[beat.id] = str(asset_path)
    
    def tearDown(self):
        """Clean up test files."""
        if self.temp_path.exists():
            shutil.rmtree(self.temp_path)
    
    def test_generate_creates_valid_fcpxml(self):
        """Test that generate() creates a valid FCPXML file."""
        output_path = self.temp_path / "test_output.fcpxml"
        
        result_path = self.generator.generate(
            self.test_beats,
            self.asset_map,
            str(output_path)
        )
        
        self.assertEqual(result_path, str(output_path))
        self.assertTrue(output_path.exists())
        self.assertGreater(output_path.stat().st_size, 0)
    
    def test_generate_creates_parseable_xml(self):
        """Test that generated FCPXML is valid XML."""
        output_path = self.temp_path / "test_output.fcpxml"
        
        self.generator.generate(
            self.test_beats,
            self.asset_map,
            str(output_path)
        )
        
        # Should parse without errors
        tree = ET.parse(str(output_path))
        root = tree.getroot()
        
        self.assertEqual(root.tag, "fcpxml")
    
    def test_fcpxml_version_is_1_8(self):
        """Test that FCPXML version attribute is 1.8."""
        output_path = self.temp_path / "test_output.fcpxml"
        
        self.generator.generate(
            self.test_beats,
            self.asset_map,
            str(output_path)
        )
        
        tree = ET.parse(str(output_path))
        root = tree.getroot()
        
        self.assertEqual(root.get("version"), "1.8")
    
    def test_resources_section_exists(self):
        """Test that resources section is present."""
        output_path = self.temp_path / "test_output.fcpxml"
        
        self.generator.generate(
            self.test_beats,
            self.asset_map,
            str(output_path)
        )
        
        tree = ET.parse(str(output_path))
        root = tree.getroot()
        
        resources = root.find("resources")
        self.assertIsNotNone(resources)
    
    def test_format_resource_exists(self):
        """Test that format resource is created."""
        output_path = self.temp_path / "test_output.fcpxml"
        
        self.generator.generate(
            self.test_beats,
            self.asset_map,
            str(output_path)
        )
        
        tree = ET.parse(str(output_path))
        resources = tree.getroot().find("resources")
        
        format_elem = resources.find("format")
        self.assertIsNotNone(format_elem)
        self.assertEqual(format_elem.get("id"), "r1")
        self.assertEqual(format_elem.get("width"), "1920")
        self.assertEqual(format_elem.get("height"), "1080")
    
    def test_asset_resources_created_for_assets(self):
        """Test that asset resources are created for each unique asset."""
        output_path = self.temp_path / "test_output.fcpxml"
        
        self.generator.generate(
            self.test_beats,
            self.asset_map,
            str(output_path)
        )
        
        tree = ET.parse(str(output_path))
        resources = tree.getroot().find("resources")
        
        asset_elements = resources.findall("asset")
        # We have 2 unique assets in this test
        self.assertEqual(len(asset_elements), 2)
        
        # Verify each asset has required attributes
        for asset in asset_elements:
            self.assertTrue(asset.get("id"))
            self.assertTrue(asset.get("name"))
            self.assertEqual(asset.get("format"), "r1")
            self.assertTrue(asset.get("duration"))
            
            # Check media-rep sub-element
            media_rep = asset.find("media-rep")
            self.assertIsNotNone(media_rep)
            self.assertTrue(media_rep.get("src").startswith("file:///"))
    
    def test_library_structure_is_valid(self):
        """Test that library/event/project/sequence hierarchy is correct."""
        output_path = self.temp_path / "test_output.fcpxml"
        
        self.generator.generate(
            self.test_beats,
            self.asset_map,
            str(output_path)
        )
        
        tree = ET.parse(str(output_path))
        root = tree.getroot()
        
        library = root.find("library")
        self.assertIsNotNone(library)
        
        event = library.find("event")
        self.assertIsNotNone(event)
        
        project = event.find("project")
        self.assertIsNotNone(project)
        
        sequence = project.find("sequence")
        self.assertIsNotNone(sequence)
    
    def test_spine_contains_clips(self):
        """Test that spine contains asset-clip elements for each beat with an asset."""
        output_path = self.temp_path / "test_output.fcpxml"
        
        self.generator.generate(
            self.test_beats,
            self.asset_map,
            str(output_path)
        )
        
        tree = ET.parse(str(output_path))
        sequence = tree.getroot().find(".//sequence")
        
        spine = sequence.find("spine")
        self.assertIsNotNone(spine)
        
        clips = spine.findall("asset-clip")
        self.assertEqual(len(clips), len(self.test_beats))
        
        # Verify clip attributes
        for clip in clips:
            self.assertTrue(clip.get("name"))
            self.assertTrue(clip.get("duration"))
            self.assertTrue(clip.get("offset"))
            self.assertRegex(clip.get("duration"), r'^\d+/\d+s$')
            self.assertTrue(clip.get("ref"))
            self.assertEqual(clip.get("start"), "0/1s")
    
    def test_generate_with_no_assets(self):
        """Test generating timeline with no assets (gaps only)."""
        output_path = self.temp_path / "test_no_assets.fcpxml"
        
        # Empty asset map
        self.generator.generate(
            self.test_beats,
            {},
            str(output_path)
        )
        
        tree = ET.parse(str(output_path))
        sequence = tree.getroot().find(".//sequence")
        
        # Should have spine with gaps
        spine = sequence.find("spine")
        gaps = spine.findall("gap")
        self.assertEqual(len(gaps), len(self.test_beats))
        
        # Should have no asset-clips
        clips = spine.findall("asset-clip")
        self.assertEqual(len(clips), 0)
        
        # Verify gap attributes
        for gap in gaps:
            self.assertTrue(gap.get("offset"))
            self.assertTrue(gap.get("duration"))
    
    def test_generate_with_empty_beats_raises_error(self):
        """Test that empty beats list raises ValueError."""
        output_path = self.temp_path / "test_output.fcpxml"
        
        with self.assertRaises(ValueError):
            self.generator.generate([], {}, str(output_path))
    
    def test_seconds_to_timecode_conversion(self):
        """Test timecode conversion for different durations."""
        # 5 seconds at 30fps = 150 frames.
        timecode_5s = self.generator._seconds_to_timecode(5.0)
        self.assertEqual(timecode_5s, "150/30s")
        
        # 0 seconds
        timecode_0s = self.generator._seconds_to_timecode(0.0)
        self.assertEqual(timecode_0s, "0/30s")
    
    def test_calculate_total_frames(self):
        """Test total frame calculation from beats."""
        total_frames = self.generator._calculate_total_frames(self.test_beats)
        
        # Calculate expected frames
        total_duration = sum(beat.duration for beat in self.test_beats)
        expected_frames = int(total_duration * 30)
        
        self.assertEqual(total_frames, expected_frames)
    
    def test_validate_xml_with_valid_structure(self):
        """Test XML validation with valid structure."""
        output_path = self.temp_path / "test_output.fcpxml"
        
        self.generator.generate(
            self.test_beats,
            self.asset_map,
            str(output_path)
        )
        
        tree = ET.parse(str(output_path))
        root = tree.getroot()
        
        # Should validate successfully
        is_valid = self.generator._validate_xml(root)
        self.assertTrue(is_valid)
    
    def test_resource_id_assignment(self):
        """Test that resource IDs are unique and sequential."""
        output_path = self.temp_path / "test_output.fcpxml"
        
        self.generator.generate(
            self.test_beats,
            self.asset_map,
            str(output_path)
        )
        
        tree = ET.parse(str(output_path))
        resources = tree.getroot().find("resources")
        
        # Format should be r1
        format_elem = resources.find("format")
        self.assertEqual(format_elem.get("id"), "r1")
        
        # Asset resources should be r2, r3, etc.
        asset_elements = resources.findall("asset")
        for i, asset in enumerate(asset_elements, start=2):
            self.assertEqual(asset.get("id"), f"r{i}")
    
    def test_generate_creates_output_directory(self):
        """Test that generate creates output directory if needed."""
        nested_path = self.temp_path / "nested" / "dir" / "output.fcpxml"
        
        self.generator.generate(
            self.test_beats,
            self.asset_map,
            str(nested_path)
        )
        
        self.assertTrue(nested_path.exists())
        self.assertTrue(nested_path.parent.exists())


class TestXMLGeneratorEdgeCases(unittest.TestCase):
    """Test edge cases and error handling in XMLGenerator."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = XMLGenerator()
        self.temp_dir = tempfile.mkdtemp(prefix="test_xml_edge_")
        self.temp_path = Path(self.temp_dir)
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        if self.temp_path.exists():
            shutil.rmtree(self.temp_path)
    
    def test_handle_very_long_beat_id(self):
        """Test handling beat with very long ID."""
        beat = Beat(
            id="beat_" + "x" * 100,
            text="This is a long enough beat text to satisfy the minimum duration requirement of three seconds.",
            stock_keyword="test",
            youtube_search_phrase="test video"
        )
        
        output_path = self.temp_path / "test.fcpxml"
        
        # Should handle gracefully
        self.generator.generate([beat], {}, str(output_path))
        self.assertTrue(output_path.exists())
    
    def test_handle_special_characters_in_text(self):
        """Test handling special characters in beat text."""
        beat = Beat(
            id="beat_001",
            text="Test with special chars: <>&\"' and unicode: Ã© Ã± Ã¼ enough words for duration.",
            stock_keyword="test special",
            youtube_search_phrase="test unicode"
        )
        
        output_path = self.temp_path / "test.fcpxml"
        
        self.generator.generate([beat], {}, str(output_path))
        
        # Should parse without errors (XML escaping handled)
        tree = ET.parse(str(output_path))
        self.assertIsNotNone(tree)
    
    def test_handle_single_beat(self):
        """Test generating timeline with single beat."""
        beat = Beat(
            id="beat_001",
            text="This is the only test beat in this timeline and it has enough words to be three seconds long.",
            stock_keyword="single test",
            youtube_search_phrase="single beat demo"
        )
        
        output_path = self.temp_path / "test.fcpxml"
        
        # Provide empty asset map - should create a gap
        self.generator.generate([beat], {}, str(output_path))
        
        tree = ET.parse(str(output_path))
        spine = tree.getroot().find(".//spine")
        gaps = spine.findall("gap")
        
        self.assertEqual(len(gaps), 1)


if __name__ == '__main__':
    unittest.main()
