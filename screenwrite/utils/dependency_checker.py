"""
Utility to check for system dependencies.
"""

import subprocess
import shutil
import sys
import re

class DependencyChecker:
    """Checks for required system tools and language runtimes."""

    def __init__(self):
        self.download_links = {
            "ffmpeg": "https://ffmpeg.org/download.html",
            "yt-dlp": "https://github.com/yt-dlp/yt-dlp#installation",
            "python": "https://www.python.org/downloads/",
            "node": "https://nodejs.org/"
        }

    def check_python_version(self, min_version=(3, 7)):
        """Check if Python version meets the minimum requirement."""
        try:
            # We can use sys.version_info directly for the current runtime,
            # but for the checker we might want to verify what 'python' points to.
            result = subprocess.run(['python', '--version'], capture_output=True, text=True, check=True)
            version_str = result.stdout.strip()
            match = re.search(r"Python (\d+)\.(\d+)", version_str)
            if match:
                major, minor = map(int, match.groups())
                return (major, minor) >= min_version
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        return False

    def check_node_version(self):
        """Check if Node.js is installed."""
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True, check=True)
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def check_ffmpeg(self):
        """Check if ffmpeg is in system PATH."""
        return shutil.which("ffmpeg") is not None

    def check_yt_dlp(self):
        """Check if yt-dlp is in system PATH."""
        return shutil.which("yt-dlp") is not None

    def get_missing_report(self):
        """Returns a list of missing dependencies and their download links."""
        report = []
        if not self.check_python_version():
            report.append(("Python 3.7+", self.download_links["python"]))
        if not self.check_node_version():
            report.append(("Node.js", self.download_links["node"]))
        if not self.check_ffmpeg():
            report.append(("ffmpeg", self.download_links["ffmpeg"]))
        if not self.check_yt_dlp():
            report.append(("yt-dlp", self.download_links["yt-dlp"]))
        return report
