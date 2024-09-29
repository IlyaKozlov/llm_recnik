"""Translate cyrillic templates to latin one"""
import os
from pathlib import Path
import cyrtranslit

template_path = Path(__file__).parent.parent / "templates"
assert template_path.exists()

latin_path = template_path / "latin"
assert latin_path.exists()
cyrillic_path = template_path / "cyrillic"
assert cyrillic_path.exists()

for name in os.listdir(latin_path):
    path = latin_path / name
    with path.open() as f:
        print(cyrtranslit.to_cyrillic(f.read(), "sr"))
