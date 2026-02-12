"""
Integration test for search preview and individual asset download.

Feature: asset-fetching-improvements
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from screenwrite.fetchers.asset_orchestrator import AssetOrchestrator, AssetCandidate

class TestSearchPreviewIntegration(unittest.TestCase):
    def test_search_to_download_flow(self):
        """Test the flow: search -> candidates -> select -> download."""
        # Use a simple class instead of MagicMock for name attribute
        class MockYouTubeClient:
            name = "YouTube"
            def __init__(self, **kwargs): pass
            search = Mock()
            download_by_id = Mock()

        class MockPexelsClient:
            name = "Pexels"
            def __init__(self, **kwargs): pass
            search = Mock()
            download_by_id = Mock()

        with patch('screenwrite.fetchers.asset_orchestrator.YouTubeClient', side_effect=MockYouTubeClient), \
             patch('screenwrite.fetchers.asset_orchestrator.PexelsClient', side_effect=MockPexelsClient), \
             patch('screenwrite.fetchers.asset_orchestrator.Path') as MockPath:
            
            # Mock Path.exists to return True
            MockPath.return_value.exists.return_value = True
            
            # Setup orchestrator inside patch
            orchestrator = AssetOrchestrator(
                youtube_enabled=True,
                pexels_enabled=True
            )
            
            # 1. Setup mocks for search
            mock_youtube = orchestrator.fetchers[0]
            mock_youtube.search.return_value = [
                {'id': 'yt1', 'title': 'YouTube Video 1', 'thumbnail_url': 't1', 'duration': 10.0, 'url': 'u1'}
            ]
            
            mock_pexels = orchestrator.fetchers[1]
            mock_pexels.search.return_value = [
                {'id': 'px1', 'title': 'Pexels Video 1', 'thumbnail_url': 't2', 'duration': 5.0, 'download_url': 'u2'}
            ]
            
            # 2. Perform search
            candidates = orchestrator.search_assets(
                youtube_query="test youtube",
                stock_query="test stock",
                duration=5.0
            )
            
            self.assertEqual(len(candidates), 2)
            self.assertEqual(candidates[0].source, "youtube")
            self.assertEqual(candidates[1].source, "pexels")
            
            # 3. Simulate selection and download
            selected_candidate = candidates[1] # Pexels
            
            # Setup mock for download
            mock_pexels.download_by_id.return_value = "/path/to/pexels_px1.mp4"
            
            # Progress tracking
            progress_updates = []
            def progress_callback(percent, status):
                progress_updates.append((percent, status))
            
            # 4. Perform download
            result_path = orchestrator.download_candidate(
                selected_candidate,
                beat_id="beat1",
                progress_callback=progress_callback
            )
            
            # 5. Verify results
            self.assertEqual(result_path, "/path/to/pexels_px1.mp4")
            mock_pexels.download_by_id.assert_called_with(
                'px1', 
                selected_candidate.metadata,
                progress_callback=progress_callback
            )

    def test_concurrent_search_operations(self):
        """Test that multiple search operations don't interfere."""
        class MockYouTubeClient:
            name = "YouTube"
            def __init__(self, **kwargs): pass
            search = Mock()
            download_by_id = Mock()

        with patch('screenwrite.fetchers.asset_orchestrator.YouTubeClient', side_effect=MockYouTubeClient):
            orchestrator = AssetOrchestrator(youtube_enabled=True, pexels_enabled=False)
            mock_youtube = orchestrator.fetchers[0]
            
            # Search 1
            mock_youtube.search.return_value = [{'id': 'v1', 'title': 'Video 1'}]
            res1 = orchestrator.search_assets("query 1", "", 5.0)
            
            # Search 2
            mock_youtube.search.return_value = [{'id': 'v2', 'title': 'Video 2'}]
            res2 = orchestrator.search_assets("query 2", "", 5.0)
            
            self.assertEqual(res1[0].id, 'v1')
            self.assertEqual(res2[0].id, 'v2')

    def test_error_recovery_and_retry(self):
        """Test that errors in one fetcher don't break others."""
        class MockYouTubeClient:
            name = "YouTube"
            def __init__(self, **kwargs): pass
            def search(self, q, count):
                raise Exception("YouTube Search Failed")
            download_by_id = Mock()

        class MockPexelsClient:
            name = "Pexels"
            def __init__(self, **kwargs): pass
            search = Mock()
            download_by_id = Mock()

        with patch('screenwrite.fetchers.asset_orchestrator.YouTubeClient', side_effect=MockYouTubeClient), \
             patch('screenwrite.fetchers.asset_orchestrator.PexelsClient', side_effect=MockPexelsClient):
            
            orchestrator = AssetOrchestrator(youtube_enabled=True, pexels_enabled=True)
            mock_pexels = orchestrator.fetchers[1]
            mock_pexels.search.return_value = [{'id': 'px1', 'title': 'Pexels Result'}]
            
            # Should fallback to Pexels even if YouTube fails
            candidates = orchestrator.search_assets("test", "test", 5.0)
            
            self.assertEqual(len(candidates), 1)
            self.assertEqual(candidates[0].source, "pexels")

    def test_concurrent_downloads(self):
        """Test that multiple individual downloads can happen concurrently."""
        import threading
        import time

        class MockFetcher:
            name = "TestFetcher"
            def __init__(self, **kwargs): pass
            def search(self, q, count): return []
            def download_by_id(self, aid, meta, progress_callback=None):
                # Simulate time-consuming download
                for i in range(1, 6):
                    if progress_callback:
                        progress_callback(i * 20, "downloading")
                    time.sleep(0.01)
                return f"/path/to/{aid}.mp4"

        with patch('screenwrite.fetchers.asset_orchestrator.YouTubeClient', side_effect=MockFetcher), \
             patch('screenwrite.fetchers.asset_orchestrator.PexelsClient', side_effect=MockFetcher), \
             patch('screenwrite.fetchers.asset_orchestrator.Path') as MockPath:
            
            MockPath.return_value.exists.return_value = True
            orchestrator = AssetOrchestrator()
            
            results = {}
            def download_worker(bid, cid, source):
                candidate = AssetCandidate(id=cid, title="T", thumbnail_url="T", duration=5.0, source=source, metadata={})
                path = orchestrator.download_candidate(candidate, beat_id=bid)
                results[bid] = path

            t1 = threading.Thread(target=download_worker, args=("b1", "c1", "testfetcher"))
            t2 = threading.Thread(target=download_worker, args=("b2", "c2", "testfetcher"))
            
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            
            self.assertEqual(results["b1"], "/path/to/c1.mp4")
            self.assertEqual(results["b2"], "/path/to/c2.mp4")

if __name__ == '__main__':
    unittest.main()
