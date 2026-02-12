import unittest
import os
import time
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock, call

from screenwrite.utils.error_handling import (
    retry_with_backoff,
    validate_markdown_file,
    ensure_output_directory,
    validate_api_key,
    check_dependency,
    ValidationResult
)

class TestErrorHandling(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    # --- retry_with_backoff Tests ---

    def test_retry_success(self):
        """Test that the function succeeds on the first try."""
        mock_func = MagicMock(return_value="success")
        mock_func.__name__ = "mock_func"
        decorated = retry_with_backoff(max_retries=3)(mock_func)

        result = decorated()

        self.assertEqual(result, "success")
        mock_func.assert_called_once()

    @patch('time.sleep')
    def test_retry_failure_then_success(self, mock_sleep):
        """Test that the function retries and succeeds."""
        mock_func = MagicMock(side_effect=[ValueError("fail"), "success"])
        mock_func.__name__ = "mock_func"
        decorated = retry_with_backoff(max_retries=3, base_delay=0.1, exceptions=(ValueError,))(mock_func)

        result = decorated()

        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 2)
        mock_sleep.assert_called_once_with(0.1)

    @patch('time.sleep')
    def test_retry_max_retries_exceeded(self, mock_sleep):
        """Test that the function raises exception after max retries."""
        mock_func = MagicMock(side_effect=ValueError("fail"))
        mock_func.__name__ = "mock_func"
        decorated = retry_with_backoff(max_retries=2, base_delay=0.1, exceptions=(ValueError,))(mock_func)

        with self.assertRaises(ValueError):
            decorated()

        self.assertEqual(mock_func.call_count, 3) # initial + 2 retries
        self.assertEqual(mock_sleep.call_count, 2)

    @patch('time.sleep')
    def test_retry_backoff_timing(self, mock_sleep):
        """Test that the delay increases with backoff factor."""
        mock_func = MagicMock(side_effect=ValueError("fail"))
        mock_func.__name__ = "mock_func"
        decorated = retry_with_backoff(max_retries=3, base_delay=1.0, backoff_factor=2.0, exceptions=(ValueError,))(mock_func)

        with self.assertRaises(ValueError):
            decorated()

        mock_sleep.assert_has_calls([call(1.0), call(2.0), call(4.0)])

    # --- validate_markdown_file Tests ---

    def test_validate_valid_file(self):
        """Test validation of a valid markdown file."""
        file_path = os.path.join(self.temp_dir, "script.md")
        with open(file_path, "w") as f:
            f.write("# Title\n\nSome content here.\n\n## Scene 1\nAction.")

        result = validate_markdown_file(file_path)

        self.assertTrue(result.is_valid)
        self.assertIsNone(result.error_message)

    def test_validate_missing_file(self):
        """Test validation of a non-existent file."""
        file_path = os.path.join(self.temp_dir, "missing.md")

        result = validate_markdown_file(file_path)

        self.assertFalse(result.is_valid)
        self.assertIn("not found", result.error_message)

    def test_validate_empty_file(self):
        """Test validation of an empty file."""
        file_path = os.path.join(self.temp_dir, "empty.md")
        with open(file_path, "w") as f:
            pass

        result = validate_markdown_file(file_path)

        self.assertFalse(result.is_valid)
        self.assertIn("empty", result.error_message)

    def test_validate_invalid_extension(self):
        """Test validation of a file with invalid extension."""
        file_path = os.path.join(self.temp_dir, "script.invalid")
        with open(file_path, "w") as f:
            f.write("# Title\nContent")

        result = validate_markdown_file(file_path)

        # It proceeds anyway but adds a warning
        self.assertTrue(result.is_valid)
        self.assertTrue(any("extension" in w for w in result.warnings))

    # --- ensure_output_directory Tests ---

    def test_ensure_output_dir_exists(self):
        """Test when output directory already exists."""
        out_dir = os.path.join(self.temp_dir, "output")
        os.makedirs(out_dir)
        file_path = os.path.join(out_dir, "video.mp4")

        result = ensure_output_directory(file_path)

        self.assertTrue(result.is_valid)

    def test_ensure_output_dir_create(self):
        """Test creation of output directory."""
        out_dir = os.path.join(self.temp_dir, "new_output")
        file_path = os.path.join(out_dir, "video.mp4")

        result = ensure_output_directory(file_path)

        self.assertTrue(result.is_valid)
        self.assertTrue(os.path.isdir(out_dir))
        self.assertTrue(any("Created output directory" in w for w in result.warnings))

    @patch('pathlib.Path.mkdir')
    def test_ensure_output_dir_permission_error(self, mock_mkdir):
        """Test handling of permission error during directory creation."""
        mock_mkdir.side_effect = PermissionError("Denied")
        out_dir = os.path.join(self.temp_dir, "protected")
        file_path = os.path.join(out_dir, "video.mp4")

        result = ensure_output_directory(file_path)

        self.assertFalse(result.is_valid)
        self.assertIn("permission denied", result.error_message)

    # --- validate_api_key Tests ---

    def test_validate_api_key_valid(self):
        """Test with a valid API key."""
        key = "valid_api_key_12345"
        result = validate_api_key(key, "Service")
        self.assertTrue(result.is_valid)

    def test_validate_api_key_invalid_type(self):
        """Test with a non-string API key."""
        result = validate_api_key(12345, "Service")
        self.assertFalse(result.is_valid)
        self.assertIn("must be a string", result.error_message)

    def test_validate_api_key_too_short(self):
        """Test with a very short API key."""
        result = validate_api_key("short", "Service")
        self.assertFalse(result.is_valid)
        self.assertIn("too short", result.error_message)

    def test_validate_api_key_placeholder(self):
        """Test with a placeholder API key."""
        result = validate_api_key("your_api_key_here", "Service")
        self.assertFalse(result.is_valid)
        self.assertIn("placeholder", result.error_message)

    # --- check_dependency Tests ---

    @patch('subprocess.run')
    def test_check_dependency_success(self, mock_run):
        """Test when dependency is available."""
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stdout = "ffmpeg version 4.2.2"
        mock_run.return_value = mock_process

        result = check_dependency("ffmpeg")

        self.assertTrue(result.is_valid)

    @patch('subprocess.run')
    def test_check_dependency_failure(self, mock_run):
        """Test when dependency check fails."""
        mock_process = MagicMock()
        mock_process.returncode = 1
        mock_run.return_value = mock_process

        result = check_dependency("unknown_tool")

        self.assertFalse(result.is_valid)
        self.assertIn("failed", result.error_message)

if __name__ == '__main__':
    unittest.main()
