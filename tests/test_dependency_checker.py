"""
Unit tests for DependencyChecker utility.
"""

import unittest
from unittest.mock import patch, MagicMock
from screenwrite.utils.dependency_checker import DependencyChecker

class TestDependencyChecker(unittest.TestCase):
    """Test cases for DependencyChecker class."""

    def setUp(self):
        """Set up test fixtures."""
        self.checker = DependencyChecker()

    @patch('subprocess.run')
    def test_check_python_version_valid(self, mock_run):
        """Test Python version check with a valid version."""
        mock_process = MagicMock()
        mock_process.stdout = "Python 3.9.5"
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        self.assertTrue(self.checker.check_python_version())

    @patch('subprocess.run')
    def test_check_python_version_invalid(self, mock_run):
        """Test Python version check with an invalid version."""
        mock_process = MagicMock()
        mock_process.stdout = "Python 3.6.8"
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        self.assertFalse(self.checker.check_python_version())

    @patch('shutil.which')
    def test_check_ffmpeg_exists(self, mock_which):
        """Test if ffmpeg existence check works."""
        mock_which.return_value = "/usr/bin/ffmpeg"
        self.assertTrue(self.checker.check_ffmpeg())

    @patch('shutil.which')
    def test_check_ffmpeg_missing(self, mock_which):
        """Test if ffmpeg missing check works."""
        mock_which.return_value = None
        self.assertFalse(self.checker.check_ffmpeg())

    @patch('shutil.which')
    def test_check_yt_dlp_exists(self, mock_which):
        """Test if yt-dlp existence check works."""
        mock_which.return_value = "/usr/local/bin/yt-dlp"
        self.assertTrue(self.checker.check_yt_dlp())

    @patch('subprocess.run')
    def test_check_node_version_valid(self, mock_run):
        """Test Node.js version check with a valid version."""
        mock_process = MagicMock()
        mock_process.stdout = "v16.14.0"
        mock_process.returncode = 0
        mock_run.return_value = mock_process
        
        self.assertTrue(self.checker.check_node_version())

if __name__ == '__main__':
    unittest.main()
