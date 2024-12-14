import os
from pathlib import Path
from typing import List
from unittest import TestCase

from flake8.api import legacy as flake8

project_root = Path(__file__).parent.parent


class TestStyle(TestCase):

    def test_style(self):
        print()
        style_guide = flake8.get_style_guide(
            ignore=['E24', 'W5'],
            select=['E', 'W', 'F'],
            format='pylint',
            max_line_length=90,
        )
        all_files = self._get_files()

        errors = style_guide.check_files(all_files)

        error_cnt = errors.total_errors
        self.assertEqual(0, error_cnt)

    def _get_files(self) -> List[str]:
        all_files: List[str] = []  # noqa
        project_roots = [project_root / "tools",
                         project_root / "tests"]
        for folder in project_roots:
            assert project_root.is_dir()
            for root, _, files in os.walk(folder):
                for file in files:
                    if file.endswith('.py') and not file.endswith("__init__.py"):
                        all_files.append(os.path.join(root, file))
        return all_files
