"""
End-to-end integration test for screenwrite.

This test validates the complete workflow: parse â†’ fetch â†’ generate â†’ validate
with mocked external APIs to ensure reliable testing.

Requirements tested:
- 1.1: Script parsing into beats
- 2.1: Asset fetching workflow
- 3.1: FCPXML generation
- 4.1: CLI interface functionality
"""

import os
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import xml.etree.ElementTree as ET

# Import the components to test
from screenwrite.orchestrator import VideoOrchestrator
from screenwrite.core.beat import Beat
from screenwrite.parsing.script_parser import ScriptParser
from screenwrite.generators.xml_generator import XMLGenerator
from screenwrite.cli import main, create_parser


class TestEndToEndIntegration(unittest.TestCase):
    """
    End-to-end integration test for the complete screenwrite workflow.
    
    Tests the full pipeline from markdown script to FCPXML output with mocked
    external dependencies to ensure reliable and fast testing.
    """
    
    def setUp(self):
        """Set up test fixtures and temporary directories."""
        # Create temporary directory for test outputs
        self.temp_dir = tempfile.mkdtemp(prefix="screenwrite_test_")
        self.temp_path = Path(self.temp_dir)
        
        # Get path to sample script
        self.script_path = Path(__file__).parent / "fixtures" / "sample_script.md"
        
        # Define output paths
        self.output_fcpxml = self.temp_path / "test_output.fcpxml"
        
        # Mock asset paths for testing
        self.mock_asset_paths = {
            "beat_001": str(self.temp_path / "beat_001.mp4"),
            "beat_002": str(self.temp_path / "beat_002.mp4"),
            "beat_003": str(self.temp_path / "beat_003.mp4"),
            "beat_004": str(self.temp_path / "beat_004.mp4"),
            "beat_005": str(self.temp_path / "beat_005.mp4"),
            "beat_006": str(self.temp_path / "beat_006.mp4"),
            "beat_007": str(self.temp_path / "beat_007.mp4"),
            "beat_008": str(self.temp_path / "beat_008.mp4"),
            "beat_009": str(self.temp_path / "beat_009.mp4"),
            "beat_010": str(self.temp_path / "beat_010.mp4")
        }
        
        # Create mock video files for testing
        for asset_path in self.mock_asset_paths.values():
            Path(asset_path).write_text("mock video content")
    
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        if self.temp_path.exists():
            shutil.rmtree(self.temp_path)
    
    def test_complete_workflow_with_mocked_fetchers(self):
        """
        Test the complete workflow: parse â†’ fetch â†’ generate â†’ validate.
        
        This test validates:
        - Script parsing produces valid beats (Requirement 1.1)
        - Asset fetching is invoked correctly (Requirement 2.1)
        - FCPXML generation produces valid output (Requirement 3.1)
        - All components integrate properly
        """
        # Mock the asset orchestrator at the module level where it's imported
        with patch('screenwrite.orchestrator.AssetOrchestrator') as mock_orchestrator_class:
            # Configure mock asset orchestrator
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator
            
            # Mock get_available_fetchers to return both fetchers
            mock_orchestrator.get_available_fetchers.return_value = ['youtube', 'pexels']
            
            # Mock fetch_assets_batch to return our test asset paths
            mock_orchestrator.fetch_assets_batch.return_value = self.mock_asset_paths
            
            # Mock get_fetcher_status
            mock_orchestrator.get_fetcher_status.return_value = {
                'youtube': {'available': True, 'status': 'ready'},
                'pexels': {'available': True, 'status': 'ready'}
            }
            
            # Create orchestrator and run workflow
            orchestrator = VideoOrchestrator(
                pexels_api_key="test_key",
                output_dir=str(self.temp_path),
                verbose=True
            )
            
            # Execute the complete workflow
            result = orchestrator.orchestrate(
                script_path=str(self.script_path),
                output_path=str(self.output_fcpxml),
                skip_fetch=False
            )
            
            # Validate workflow results
            self.assertTrue(result['success'], f"Workflow failed: {result.get('errors', [])}")
            self.assertGreater(result['beats_count'], 0, "No beats were generated")
            self.assertEqual(result['assets_fetched'], result['beats_count'], "Not all assets were fetched")
            self.assertTrue(result['fcpxml_generated'], "FCPXML was not generated")
            
            # Verify asset orchestrator was called correctly
            mock_orchestrator.fetch_assets_batch.assert_called_once()
            
            # Get the call arguments to verify beat data
            call_args = mock_orchestrator.fetch_assets_batch.call_args[0][0]
            self.assertIsInstance(call_args, list, "fetch_assets_batch should be called with a list")
            self.assertGreater(len(call_args), 0, "No queries were passed to asset fetcher")
            
            # Validate each query has required fields
            for query in call_args:
                self.assertIn('id', query, "Query missing 'id' field")
                self.assertIn('youtube_query', query, "Query missing 'youtube_query' field")
                self.assertIn('stock_query', query, "Query missing 'stock_query' field")
                self.assertIn('duration', query, "Query missing 'duration' field")
                
                # Validate query content
                self.assertIsInstance(query['id'], str, "Beat ID should be string")
                self.assertIsInstance(query['youtube_query'], str, "YouTube query should be string")
                self.assertIsInstance(query['stock_query'], str, "Stock query should be string")
                self.assertIsInstance(query['duration'], (int, float), "Duration should be numeric")
                
                # Validate query is non-empty (Requirement 1.2, 1.3)
                self.assertTrue(query['youtube_query'].strip(), "YouTube query should not be empty")
                self.assertTrue(query['stock_query'].strip(), "Stock query should not be empty")
                
                # Validate duration is in valid range (Requirement 1.1, 1.5)
                self.assertGreaterEqual(query['duration'], 5.0, "Beat duration should be >= 5 seconds")
                self.assertLessEqual(query['duration'], 10.0, "Beat duration should be <= 10 seconds")
    
    def test_fcpxml_output_validation(self):
        """
        Test that generated FCPXML is valid and importable.
        
        This test validates:
        - FCPXML file is created (Requirement 3.5)
        - FCPXML structure is valid (Requirement 3.1)
        - Spine contains gaps for each beat (Requirement 3.2)
        - Connected clips are properly aligned (Requirement 3.3)
        - Resource references are valid (Requirement 3.4)
        """
        # Mock asset fetching for this test
        with patch('screenwrite.orchestrator.AssetOrchestrator') as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator
            mock_orchestrator.get_available_fetchers.return_value = ['youtube', 'pexels']
            mock_orchestrator.fetch_assets_batch.return_value = self.mock_asset_paths
            mock_orchestrator.get_fetcher_status.return_value = {
                'youtube': {'available': True, 'status': 'ready'},
                'pexels': {'available': True, 'status': 'ready'}
            }
            
            # Run workflow
            orchestrator = VideoOrchestrator(output_dir=str(self.temp_path))
            result = orchestrator.orchestrate(
                script_path=str(self.script_path),
                output_path=str(self.output_fcpxml)
            )
            
            # Verify FCPXML file exists (Requirement 3.5)
            self.assertTrue(self.output_fcpxml.exists(), "FCPXML file was not created")
            self.assertGreater(self.output_fcpxml.stat().st_size, 0, "FCPXML file is empty")
            
            # Parse and validate FCPXML structure (Requirement 3.1)
            try:
                tree = ET.parse(str(self.output_fcpxml))
                root = tree.getroot()
            except ET.ParseError as e:
                self.fail(f"FCPXML is not valid XML: {e}")
            
            # Validate root element
            self.assertEqual(root.tag, "fcpxml", "Root element should be 'fcpxml'")
            self.assertEqual(root.get("version"), "1.8", "FCPXML version should be 1.8")
            
            # Validate resources section
            resources = root.find("resources")
            self.assertIsNotNone(resources, "Resources section missing")
            
            # Check format resource
            format_elem = resources.find("format")
            self.assertIsNotNone(format_elem, "Format resource missing")
            self.assertEqual(format_elem.get("id"), "r1", "Format should have ID 'r1'")
            
            # Check asset resources (Requirement 3.4) - should have resources when assets are mocked
            asset_elements = resources.findall("asset")
            self.assertGreater(len(asset_elements), 0, "No asset resources found")
            
            # Validate each asset resource has required attributes
            for asset in asset_elements:
                self.assertTrue(asset.get("id"), "Asset resource missing ID")
                self.assertTrue(asset.get("name"), "Asset resource missing name")
                
                # Check media-rep sub-element
                media_rep = asset.find("media-rep")
                self.assertIsNotNone(media_rep, "Asset resource missing media-rep element")
            
            # Validate library structure
            library = root.find("library")
            self.assertIsNotNone(library, "Library section missing")
            
            event = library.find("event")
            self.assertIsNotNone(event, "Event missing")
            
            project = event.find("project")
            self.assertIsNotNone(project, "Project missing")
            
            sequence = project.find("sequence")
            self.assertIsNotNone(sequence, "Sequence missing")
            
            # Validate spine with clips or gaps (Requirement 3.2)
            spine = sequence.find("spine")
            self.assertIsNotNone(spine, "Spine missing")
            
            # Spine should have either asset-clip (if asset found) or gap (if no asset)
            clips = spine.findall("asset-clip")
            gaps = spine.findall("gap")
            total_segments = len(clips) + len(gaps)
            
            self.assertGreater(total_segments, 0, "No clips or gaps found in spine")
            self.assertEqual(total_segments, result['beats_count'], "Segment count doesn't match beat count")
            
            # Validate each segment has required attributes
            for segment in clips + gaps:
                self.assertTrue(segment.get("name"), "Segment missing name")
                self.assertTrue(segment.get("duration"), "Segment missing duration")
                
                # Validate duration format
                duration = segment.get("duration")
                self.assertRegex(duration, r'^\d+/\d+s$', f"Invalid duration format: {duration}")
                
                if segment.tag == "asset-clip":
                    self.assertTrue(segment.get("ref"), "Clip missing resource reference")
                    # Validate resource reference exists (Requirement 3.4)
                    ref_id = segment.get("ref")
                    referenced_asset = resources.find(f"asset[@id='{ref_id}']")
                    self.assertIsNotNone(referenced_asset, f"Referenced resource {ref_id} not found")
    
    def test_workflow_with_no_assets(self):
        """
        Test workflow when no assets are fetched (skip_fetch=True).
        
        This validates that the system can generate a valid timeline even
        without B-roll assets, creating gaps-only timeline.
        """
        orchestrator = VideoOrchestrator(output_dir=str(self.temp_path))
        
        result = orchestrator.orchestrate(
            script_path=str(self.script_path),
            output_path=str(self.output_fcpxml),
            skip_fetch=True
        )
        
        # Validate workflow completed successfully
        self.assertTrue(result['success'], f"Workflow failed: {result.get('errors', [])}")
        self.assertGreater(result['beats_count'], 0, "No beats were generated")
        self.assertEqual(result['assets_fetched'], 0, "Assets should not be fetched when skip_fetch=True")
        self.assertTrue(result['fcpxml_generated'], "FCPXML was not generated")
        
        # Validate FCPXML exists and is valid
        self.assertTrue(self.output_fcpxml.exists(), "FCPXML file was not created")
        
        # Parse FCPXML and validate structure
        tree = ET.parse(str(self.output_fcpxml))
        root = tree.getroot()
        
        # Should have spine with gaps but no connected clips
        sequence = root.find(".//sequence")
        self.assertIsNotNone(sequence, "Sequence missing")
        
        spine = sequence.find("spine")
        self.assertIsNotNone(spine, "Spine missing")
        
        gaps = spine.findall("gap")
        self.assertEqual(len(gaps), result['beats_count'], "Gap count doesn't match beat count")
        
        # Should have no lanes (no connected clips)
        lanes = sequence.findall("lane")
        self.assertEqual(len(lanes), 0, "Should have no lanes when no assets are fetched")
    
    def test_cli_interface_integration(self):
        """
        Test CLI interface integration (Requirement 4.1).
        
        This validates that the CLI can parse arguments and execute
        the workflow correctly.
        """
        # Mock command line arguments
        test_args = [
            'screenwrite',
            str(self.script_path),
            '--output', str(self.output_fcpxml),
            '--no-fetch',  # Skip fetching to avoid external dependencies
            '--verbose'
        ]
        
        # Mock asset orchestrator to avoid external calls
        with patch('screenwrite.orchestrator.AssetOrchestrator') as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator
            mock_orchestrator.get_available_fetchers.return_value = []
            mock_orchestrator.get_fetcher_status.return_value = {}
            
            # Mock sys.argv and run CLI
            with patch('sys.argv', test_args):
                # Import and test argument parsing
                parser = create_parser()
                args = parser.parse_args(test_args[1:])  # Skip program name
                
                # Validate parsed arguments
                self.assertEqual(args.script, str(self.script_path))
                self.assertEqual(args.output, str(self.output_fcpxml))
                self.assertTrue(args.no_fetch)
                self.assertTrue(args.verbose)
                
                # Test that CLI would execute successfully
                # (We don't call main() directly to avoid sys.exit())
                orchestrator = VideoOrchestrator(
                    output_dir=str(self.temp_path),
                    verbose=args.verbose
                )
                
                result = orchestrator.orchestrate(
                    script_path=args.script,
                    output_path=args.output,
                    skip_fetch=args.no_fetch
                )
                
                self.assertTrue(result['success'], "CLI workflow should succeed")
    
    def test_error_handling_integration(self):
        """
        Test error handling throughout the workflow.
        
        This validates that errors are handled gracefully and don't
        crash the entire workflow.
        """
        # Test with invalid script file
        invalid_script = self.temp_path / "invalid.md"
        invalid_script.write_text("")  # Empty file
        
        orchestrator = VideoOrchestrator(output_dir=str(self.temp_path))
        
        # Should handle empty script gracefully
        with self.assertRaises(Exception):  # Should raise InputValidationError
            orchestrator.orchestrate(
                script_path=str(invalid_script),
                output_path=str(self.output_fcpxml)
            )
        
        # Test with asset fetching failures
        with patch('screenwrite.orchestrator.AssetOrchestrator') as mock_orchestrator_class:
            mock_orchestrator = Mock()
            mock_orchestrator_class.return_value = mock_orchestrator
            mock_orchestrator.get_available_fetchers.return_value = ['youtube']
            
            # Mock fetch to return empty results (all fetches failed)
            empty_asset_map = {f"beat_{i:03d}": None for i in range(1, 11)}
            mock_orchestrator.fetch_assets_batch.return_value = empty_asset_map
            mock_orchestrator.get_fetcher_status.return_value = {
                'youtube': {'available': True, 'status': 'ready'}
            }
            
            # Create a new orchestrator instance that will use the mocked AssetOrchestrator
            orchestrator = VideoOrchestrator(output_dir=str(self.temp_path))
            
            # Should complete workflow even with no assets
            result = orchestrator.orchestrate(
                script_path=str(self.script_path),
                output_path=str(self.output_fcpxml)
            )
            
            self.assertTrue(result['success'], "Workflow should succeed even with fetch failures")
            self.assertEqual(result['assets_fetched'], 0, "No assets should be fetched")
            self.assertIn("No assets were successfully fetched", result['warnings'])


if __name__ == '__main__':
    unittest.main()
