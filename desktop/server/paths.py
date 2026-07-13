"""Filesystem anchors for the desktop app.

Everything derives from the location of this file (the repo the app runs
from) and the user's home. The app's runtime data lives OUTSIDE the repo in
~/.screenwrite so runs survive branch switches and never dirty the checkout.
"""

import socket
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# The interpreter running the server is the venv's; its Scripts dir holds the
# python.exe used to spawn runner child processes.
VENV_PYTHON = Path(sys.executable).parent / (
    "python.exe" if sys.platform.startswith("win") else "python"
)

APP_HOME = Path.home() / ".screenwrite"


def runs_dir() -> Path:
    path = APP_HOME / "runs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def new_run_id() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def new_run_dir(run_id: str) -> Path:
    path = runs_dir() / run_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def default_media_dir() -> Path:
    """Persistent download location so FCPXML/Resolve links never dangle."""
    path = APP_HOME / "media"
    path.mkdir(parents=True, exist_ok=True)
    return path


def free_port() -> int:
    """Ask the OS for a free localhost port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]
