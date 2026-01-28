"""
Unit tests for EnvManager utility.
"""

import unittest
import tempfile
import shutil
from pathlib import Path
from screenwrite.utils.env_manager import EnvManager

class TestEnvManager(unittest.TestCase):
    """Test cases for EnvManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
        self.env_manager = EnvManager(base_path=self.temp_path)

    def tearDown(self):
        """Clean up test files."""
        shutil.rmtree(self.temp_dir)

    def test_ensure_env_exists_creates_from_example(self):
        """Test that .env is created if it doesn't exist but .env.example does."""
        example_path = self.temp_path / ".env.example"
        example_path.write_text("API_KEY=template\nDEBUG=True")
        
        env_path = self.temp_path / ".env"
        self.assertFalse(env_path.exists())
        
        self.env_manager.ensure_env_exists(".env.example", ".env")
        
        self.assertTrue(env_path.exists())
        self.assertEqual(env_path.read_text(), "API_KEY=template\nDEBUG=True")

    def test_update_env_key(self):
        """Test updating a specific key in the .env file."""
        env_path = self.temp_path / ".env"
        env_path.write_text("GEMINI_API_KEY=old_key\nOTHER_VAR=value")
        
        self.env_manager.update_env_key(env_path, "GEMINI_API_KEY", "new_secret_key")
        
        content = env_path.read_text()
        self.assertIn("GEMINI_API_KEY=new_secret_key", content)
        self.assertIn("OTHER_VAR=value", content)

if __name__ == '__main__':
    unittest.main()
