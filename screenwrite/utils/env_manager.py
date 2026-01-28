"""
Utility to manage .env files and environment configuration.
"""

import os
import shutil
from pathlib import Path

class EnvManager:
    """Manages creation and updating of .env files."""

    def __init__(self, base_path=None):
        self.base_path = Path(base_path) if base_path else Path.cwd()

    def ensure_env_exists(self, example_name=".env.example", env_name=".env"):
        """Ensures a .env file exists, creating it from an example if necessary."""
        example_path = self.base_path / example_name
        env_path = self.base_path / env_name

        if not env_path.exists() and example_path.exists():
            shutil.copy(str(example_path), str(env_path))
            return True
        return env_path.exists()

    def update_env_key(self, env_path, key, value):
        """Updates or adds a key-value pair in a .env file."""
        env_path = Path(env_path)
        if not env_path.exists():
            env_path.write_text(f"{key}={value}\n")
            return

        lines = env_path.read_text().splitlines()
        new_lines = []
        found = False
        
        for line in lines:
            if line.startswith(f"{key}="):
                new_lines.append(f"{key}={value}")
                found = True
            else:
                new_lines.append(line)
        
        if not found:
            new_lines.append(f"{key}={value}")
            
        env_path.write_text("\n".join(new_lines) + "\n")

    def prompt_for_key(self, prompt_text="Please enter your Gemini API key: "):
        """Interactively prompt user for an API key."""
        # This is a helper for the actual CLI scripts
        try:
            key = input(prompt_text).strip()
            return key
        except EOFError:
            return ""
