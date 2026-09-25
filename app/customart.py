"""Support for per-card custom artwork supplied by the user.

Cards without a custom image fall back to the auto-generated SVG in
cardart.py. A custom image is looked up by card code + a known extension
inside static/img/custom_cards/, e.g. static/img/custom_cards/OP14-096.jpg
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

CUSTOM_ART_EXTENSIONS = ("jpg", "jpeg", "png", "webp")


def find_custom_art_filename(code: str, custom_dir: Path) -> Optional[str]:
    """Return the filename (not path) of a custom art image for this card
    code, if one exists in custom_dir, else None."""
    for ext in CUSTOM_ART_EXTENSIONS:
        candidate = custom_dir / f"{code}.{ext}"
        if candidate.is_file():
            return candidate.name
    return None
