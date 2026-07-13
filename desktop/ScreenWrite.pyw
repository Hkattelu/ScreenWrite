"""Double-clickable ScreenWrite Desktop launcher (pythonw = no console)."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from desktop.app import main  # noqa: E402

sys.exit(main())
