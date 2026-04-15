"""Design guide loader — reads markdown guides from the `guides/` directory.

Builds a mapping `DESIGN_GUIDES: Dict[str, str]` where the key is the
topic slug (filename without `.md`) and the value is the file contents.
"""
from pathlib import Path
from typing import Dict

GUIDES_DIR = Path(__file__).parent / "guides"

DESIGN_GUIDES: Dict[str, str] = {}

if GUIDES_DIR.exists() and GUIDES_DIR.is_dir():
    for p in GUIDES_DIR.iterdir():
        if p.suffix.lower() != ".md":
            continue
        topic = p.stem
        try:
            DESIGN_GUIDES[topic] = p.read_text(encoding="utf-8")
        except Exception:
            # Ignore unreadable files but keep process running
            pass
