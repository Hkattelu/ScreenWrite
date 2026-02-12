import unittest
from unittest.mock import MagicMock, patch
import os
import tempfile
from pathlib import Path
import logging

# Import the module to be tested
try:
    from screenwrite.fetchers.youtube_client import YouTubeClient, NetworkError
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from screenwrite.fetchers.youtube_client import YouTubeClient, NetworkError

class TestYouTubeClient(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for tests
        self.test_dir_obj = tempfile.TemporaryDirectory()
        self.test_dir = self.test_dir_obj.name

        # Patch yt_dlp at the module level
        self.patcher_yt_dlp = patch('screenwrite.fetchers.youtube_client.yt_dlp')
        self.mock_yt_dlp = self.patcher_yt_dlp.start()

        # Define a proper Exception class for DownloadError so try/except blocks work as expected
        # and str(e) returns the message
        class MockDownloadError(Exception):
            pass
        self.mock_yt_dlp.utils.DownloadError = MockDownloadError

        # Setup common mocks
        self.mock_logger = patch('screenwrite.fetchers.youtube_client.logger').start()

        # Mock shutil.which to simulate ffmpeg availability
        self.patcher_shutil = patch('shutil.which')
        self.mock_shutil_which = self.patcher_shutil.start()
        self.mock_shutil_which.return_value = '/usr/bin/ffmpeg'

        # Mock subprocess.run for ffmpeg version check
        self.patcher_subprocess = patch('subprocess.run')
        self.mock_subprocess = self.patcher_subprocess.start()
        self.mock_subprocess.return_value.returncode = 0

    def tearDown(self):
        self.patcher_yt_dlp.stop()
        patch.stopall()
        # Clean up temp dir
        self.test_dir_obj.cleanup()

    # --- Initialization Tests ---

    def test_init_defaults(self):
        """Test default initialization."""
        client = YouTubeClient()
        self.assertTrue(client._yt_dlp_available)
        self.assertTrue(client._ffmpeg_available)
        self.assertEqual(client.name, "YouTube")
        # Default output dir should be temp dir
        self.assertEqual(client.output_dir, Path(tempfile.gettempdir()))

    def test_init_with_output_dir(self):
        """Test initialization with custom output directory."""
        client = YouTubeClient(output_dir=self.test_dir)
        self.assertEqual(client.output_dir, Path(self.test_dir))

    def test_init_no_yt_dlp(self):
        """Test initialization when yt_dlp is missing."""
        with patch('screenwrite.fetchers.youtube_client.yt_dlp', None):
            client = YouTubeClient()
            self.assertFalse(client._yt_dlp_available)

    def test_init_no_ffmpeg(self):
        """Test initialization when ffmpeg is missing."""
        self.mock_shutil_which.return_value = None
        client = YouTubeClient()
        self.assertFalse(client._ffmpeg_available)

    # --- Search Tests ---

    def test_search_success(self):
        """Test successful search."""
        client = YouTubeClient()
        # Mock the context manager returned by YoutubeDL()
        mock_ydl_instance = self.mock_yt_dlp.YoutubeDL.return_value.__enter__.return_value
        mock_ydl_instance.extract_info.return_value = {
            'entries': [{'url': 'http://youtube.com/watch?v=123'}]
        }

        urls = client._search("test query")
        self.assertEqual(urls, ['http://youtube.com/watch?v=123'])

    def test_search_no_results(self):
        """Test search with no results."""
        client = YouTubeClient()
        mock_ydl_instance = self.mock_yt_dlp.YoutubeDL.return_value.__enter__.return_value
        mock_ydl_instance.extract_info.return_value = {'entries': []}

        urls = client._search("test query")
        self.assertIsNone(urls)

    def test_search_network_error(self):
        """Test search handling network error."""
        client = YouTubeClient()
        mock_ydl_instance = self.mock_yt_dlp.YoutubeDL.return_value.__enter__.return_value

        # Mock DownloadError using the custom exception class we injected
        error = self.mock_yt_dlp.utils.DownloadError("Network error")
        mock_ydl_instance.extract_info.side_effect = error

        with self.assertRaises(NetworkError):
            client._search("test query")

    # --- Download Tests ---

    def test_download_success(self):
        """Test successful download."""
        client = YouTubeClient(output_dir=self.test_dir)
        mock_ydl_instance = self.mock_yt_dlp.YoutubeDL.return_value.__enter__.return_value
        mock_ydl_instance.extract_info.return_value = {'id': '123', 'ext': 'mp4'}

        expected_path = os.path.join(self.test_dir, "video.mp4")
        mock_ydl_instance.prepare_filename.return_value = expected_path

        # Mock file existence
        with patch('os.path.exists', return_value=True):
            path = client._download("http://url", "query")
            self.assertEqual(path, expected_path)

    def test_download_failure_file_not_found(self):
        """Test download where file is not found after download reported success."""
        client = YouTubeClient(output_dir=self.test_dir)
        mock_ydl_instance = self.mock_yt_dlp.YoutubeDL.return_value.__enter__.return_value
        mock_ydl_instance.extract_info.return_value = {'id': '123'}
        mock_ydl_instance.prepare_filename.return_value = "missing_file.mp4"

        with patch('os.path.exists', return_value=False):
            path = client._download("http://url", "query")
            self.assertIsNone(path)

    def test_download_fallback_when_empty(self):
        """Test download fallback logic when first attempt yields empty file."""
        client = YouTubeClient(output_dir=self.test_dir)
        client._ffmpeg_available = True # Force ffmpeg available to trigger merge logic path

        mock_ydl_instance = self.mock_yt_dlp.YoutubeDL.return_value.__enter__.return_value

        # First call raises DownloadError with "empty"
        # Second call succeeds
        error = self.mock_yt_dlp.utils.DownloadError("file is empty")

        # We simulate:
        # 1. extract_info raises error
        # 2. extract_info returns info
        mock_ydl_instance.extract_info.side_effect = [error, {'id': '123'}]
        mock_ydl_instance.prepare_filename.return_value = "video.mp4"

        with patch('os.path.exists', return_value=True):
            path = client._download("http://url", "query")
            # Should succeed on second try
            self.assertEqual(path, "video.mp4")
            # Should have called extract_info twice
            self.assertEqual(mock_ydl_instance.extract_info.call_count, 2)

    # --- Trim Tests ---

    def test_trim_success(self):
        """Test successful video trimming."""
        client = YouTubeClient()
        client._ffmpeg_available = True

        with patch('subprocess.run') as mock_run,              patch('os.path.exists', return_value=True),              patch('os.path.getsize', return_value=1024),              patch('os.remove'):

            mock_run.return_value.returncode = 0

            # Provide a dummy input path
            input_path = os.path.join(self.test_dir, "input.mp4")
            result = client._trim_video(input_path, 10.0)

            self.assertIsNotNone(result)
            self.assertTrue("trimmed_input.mp4" in result)
            mock_run.assert_called()

    def test_trim_ffmpeg_unavailable(self):
        """Test trimming when ffmpeg is unavailable."""
        client = YouTubeClient()
        client._ffmpeg_available = False

        result = client._trim_video("input.mp4", 10.0)
        self.assertIsNone(result)

    def test_trim_subprocess_failure(self):
        """Test trimming when ffmpeg fails."""
        client = YouTubeClient()
        client._ffmpeg_available = True

        with patch('subprocess.run') as mock_run:
            mock_run.return_value.returncode = 1 # Error code

            result = client._trim_video("input.mp4", 10.0)
            self.assertIsNone(result)

    # --- Fetch Integration Tests ---

    def test_fetch_full_flow(self):
        """Test the full fetch flow (search -> download -> trim)."""
        client = YouTubeClient()
        client._ffmpeg_available = True

        # We need to mock the retry wrappers or the internal methods.
        # Since the class wraps methods with @retry_with_backoff at definition time,
        # we can patch the methods on the instance.

        with patch.object(client, '_search_with_retry', return_value=["http://url"]) as mock_search, \
             patch.object(client, '_download_with_retry', return_value="video.mp4") as mock_download, \
             patch.object(client, '_trim_video_with_retry', return_value="trimmed.mp4") as mock_trim, \
             patch('os.remove') as mock_remove:

            result = client.fetch("query", 10.0)

            self.assertEqual(result, "trimmed.mp4")
            mock_search.assert_called_with("query", count=1)
            mock_download.assert_called_with("http://url", "query_0")
            mock_trim.assert_called_with("video.mp4", 10.0)
            # Should verify original file removal
            mock_remove.assert_called_with("video.mp4")

    def test_fetch_no_ffmpeg_fallback(self):
        """Test fetch flow fallback when ffmpeg is missing."""
        client = YouTubeClient()
        client._ffmpeg_available = False

        with patch.object(client, '_search_with_retry', return_value=["http://url"]), \
             patch.object(client, '_download_with_retry', return_value="video.mp4"), \
             patch.object(client, '_trim_video_with_retry') as mock_trim:

            result = client.fetch("query", 10.0)

            self.assertEqual(result, "video.mp4")
            mock_trim.assert_not_called()

    def test_fetch_search_fails(self):
        """Test fetch when search returns no results."""
        client = YouTubeClient()

        with patch.object(client, '_search_with_retry', return_value=None):
            result = client.fetch("query", 10.0)
            self.assertIsNone(result)

    def test_fetch_download_fails(self):
        """Test fetch when download fails."""
        client = YouTubeClient()

        with patch.object(client, '_search_with_retry', return_value=["http://url"]), \
             patch.object(client, '_download_with_retry', return_value=None):
            result = client.fetch("query", 10.0)
            self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
