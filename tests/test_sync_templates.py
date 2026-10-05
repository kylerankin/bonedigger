"""Unit tests for the issue-template sync step.

Exercises the same copy-and-validate that
``.github/workflows/sync-templates.yml`` performs: it copies every ``*.yml``
under ``templates/`` into a downstream ``.github/ISSUE_TEMPLATE/`` directory
and relies on those files being valid GitHub issue-template YAML.
"""

import tempfile
import unittest
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
TEMPLATES = REPO_ROOT / "templates"


def sync_templates(src=TEMPLATES, dst=None):
    """Replicate sync-templates.yml's copy step into a fresh directory.

    Mirrors the workflow's ``mkdir -p`` + ``cp templates/*.yml`` and returns
    the destination directory (standing in for the downstream checkout).
    """
    if dst is None:
        dst = Path(tempfile.mkdtemp()) / "downstream" / ".github" / "ISSUE_TEMPLATE"
    dst.mkdir(parents=True, exist_ok=True)
    for yml in src.glob("*.yml"):
        dst.joinpath(yml.name).write_text(yml.read_text())
    return dst


class TemplateSyncTests(unittest.TestCase):
    def setUp(self):
        self.dst = sync_templates()

    def test_all_templates_copied(self):
        expected = {p.name for p in TEMPLATES.glob("*.yml")}
        copied = {p.name for p in self.dst.glob("*.yml")}
        self.assertEqual(expected, copied)
        self.assertGreater(len(copied), 0)

    def test_copied_files_are_identical(self):
        for yml in TEMPLATES.glob("*.yml"):
            with self.subTest(file=yml.name):
                self.assertEqual(
                    (self.dst / yml.name).read_text(), yml.read_text()
                )

    def test_copied_templates_parse_as_yaml(self):
        for yml in self.dst.glob("*.yml"):
            with self.subTest(file=yml.name):
                data = yaml.safe_load(yml.read_text())
                self.assertIsInstance(data, dict)

    def test_source_templates_parse_as_yaml(self):
        for yml in TEMPLATES.glob("*.yml"):
            with self.subTest(file=yml.name):
                data = yaml.safe_load(yml.read_text())
                self.assertIsInstance(data, dict)


if __name__ == "__main__":
    unittest.main()
