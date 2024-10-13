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

for name in os.listdir(cyrillic_path):
    path = cyrillic_path / name
    path_out = latin_path / name
    with path.open() as f, open(path_out, "w") as w:
        w.write(cyrtranslit.to_latin(f.read(), "sr"))