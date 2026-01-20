"""
Unit tests for XMLGenerator module.

Tests FCPXML 1.8 generation, validation, and structure.
"""

import unittest
import shutil
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from vid_orchestrator.generators.xml_generator import XMLGenerator
from vid_orchestrator.core.beat import Beat


class TestXMLGenerator(unittest.TestCase):
    """Test cases for XMLGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.generator = XMLGenerator(framerate=30)
        self.temp_dir = tempfile.mkdtemp(prefix="test_xml_")
        self.temp_path = Path(self.temp_dir)
        
        # Create test beats
        self.test_beats = [
            Beat(
                id="beat_001",
                text="This is the first test beat with enough words.",
                stock_keyword="test coding",
                youtube_search_phrase="test programming tutorial"
            ),
            Beat(
                id="beat_002", 
                text="This is the second test beat also with enough words.",
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
    
    def test_media_resources_created_for_assets(self):
        """Test that media resources are created for each asset."""
        output_path = self.temp_path / "test_output.fcpxml"
        
        self.generator.generate(
            self.test_beats,
            self.asset_map,
            str(output_path)
        )
        
        tree = ET.parse(str(output_path))
        resources = tree.getroot().find("resources")
        
        media_elements = resources.findall("media")
        self.assertEqual(len(media_elements), len(self.asset_map))
        
        # Verify each media has required attributes
        for media in media_elements:
            self.assertTrue(media.get("id"))
            self.assertTrue(media.get("name"))
            
            # Check asset sub-element
            asset = media.find("asset")
            self.assertIsNotNone(asset)
    
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
    
    def test_spine_contains_gaps(self):
        """Test that spine contains gap elements for each beat."""
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
        
        gaps = spine.findall("gap")
        self.assertEqual(len(gaps), len(self.test_beats))
        
        # Verify gap attributes
        for gap in gaps:
            self.assertTrue(gap.get("name"))
            self.assertTrue(gap.get("duration"))
            self.assertRegex(gap.get("duration"), r'^\d+/\d+s$')
    
    def test_lane_contains_connected_clips(self):
        """Test that Lane 1 contains connected clips for B-roll."""
        output_path = self.temp_path / "test_output.fcpxml"
        
        self.generator.generate(
            self.test_beats,
            self.asset_map,
            str(output_path)
        )
        
        tree = ET.parse(str(output_path))
        sequence = tree.getroot().find(".//sequence")
        
        lanes = sequence.findall("lane")
        self.assertGreater(len(lanes), 0)
        
        # Find Lane 1
        lane1 = None
        for lane in lanes:
            if lane.get("index") == "1":
                lane1 = lane
                break
        
        self.assertIsNotNone(lane1, "Lane 1 should exist")
        
        clips = lane1.findall("clip")
        self.assertEqual(len(clips), len(self.asset_map))
        
        # Verify clip attributes
        for clip in clips:
            self.assertTrue(clip.get("name"))
            self.assertTrue(clip.get("ref"))
            self.assertTrue(clip.get("offset"))
            self.assertTrue(clip.get("duration"))
    
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
        
        # Should have no lanes (no connected clips)
        lanes = sequence.findall("lane")
        self.assertEqual(len(lanes), 0)
    
    def test_generate_with_empty_beats_raises_error(self):
        """Test that empty beats list raises ValueError."""
        output_path = self.temp_path / "test_output.fcpxml"
        
        with self.assertRaises(ValueError):
            self.generator.generate([], {}, str(output_path))
    
    def test_seconds_to_timecode_conversion(self):
        """Test timecode conversion for different durations."""
        # 5 seconds at 30fps = 150 frames
        timecode_5s = self.generator._seconds_to_timecode(5.0)
        self.assertEqual(timecode_5s, "150/30s")
        
        # 10 seconds at 30fps = 300 frames
        timecode_10s = self.generator._seconds_to_timecode(10.0)
        self.assertEqual(timecode_10s, "300/30s")
        
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
        
        # Media resources should be r2, r3, etc.
        media_elements = resources.findall("media")
        for i, media in enumerate(media_elements, start=2):
            self.assertEqual(media.get("id"), f"r{i}")
    
    def test_clip_offsets_are_cumulative(self):
        """Test that clip offsets accumulate properly."""
        output_path = self.temp_path / "test_output.fcpxml"
        
        self.generator.generate(
            self.test_beats,
            self.asset_map,
            str(output_path)
        )
        
        tree = ET.parse(str(output_path))
        sequence = tree.getroot().find(".//sequence")
        lane = sequence.find("lane[@index='1']")
        
        clips = lane.findall("clip")
        
        # First clip should start at 0
        first_offset = clips[0].get("offset")
        self.assertEqual(first_offset, "0/30s")
        
        # Subsequent clips should have cumulative offsets
        cumulative_duration = 0.0
        for i, clip in enumerate(clips):
            expected_offset = self.generator._seconds_to_timecode(cumulative_duration)
            actual_offset = clip.get("offset")
            self.assertEqual(actual_offset, expected_offset)
            cumulative_duration += self.test_beats[i].duration
    
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
            text="This is a test beat with a very long identifier string.",
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
            text="Test with special chars: <>&\"' and unicode: é ñ ü",
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
            text="This is the only test beat in this timeline.",
            stock_keyword="single test",
            youtube_search_phrase="single beat demo"
        )
        
        output_path = self.temp_path / "test.fcpxml"
        
        self.generator.generate([beat], {}, str(output_path))
        
        tree = ET.parse(str(output_path))
        spine = tree.getroot().find(".//spine")
        gaps = spine.findall("gap")
        
        self.assertEqual(len(gaps), 1)
    
    def test_handle_many_beats(self):
        """Test generating timeline with many beats."""
        beats = []
        for i in range(50):
            beat = Beat(
                id=f"beat_{i:03d}",
                text=f"This is test beat number {i} with sufficient word count.",
                stock_keyword=f"test {i}",
                youtube_search_phrase=f"test video {i}"
            )
            beats.append(beat)
        
        output_path = self.temp_path / "test.fcpxml"
        
        self.generator.generate(beats, {}, str(output_path))
        
        tree = ET.parse(str(output_path))
        spine = tree.getroot().find(".//spine")
        gaps = spine.findall("gap")
        
        self.assertEqual(len(gaps), 50)


if __name__ == '__main__':
    unittest.main()
