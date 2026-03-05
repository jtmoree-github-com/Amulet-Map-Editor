import importlib
import py_compile
import unittest
from pathlib import Path


class StartupSafetyTestCase(unittest.TestCase):
    def test_source_files_compile(self):
        project_root = Path(__file__).resolve().parents[1]
        source_root = project_root / "amulet_map_editor"

        python_files = sorted(source_root.rglob("*.py"))
        self.assertTrue(python_files, "No Python source files found to compile.")

        for file_path in python_files:
            py_compile.compile(str(file_path), doraise=True)

    def test_edit_modules_import(self):
        importlib.import_module("amulet_map_editor.programs.edit.edit")
        importlib.import_module("amulet_map_editor.programs.edit.api.canvas.edit_canvas")


if __name__ == "__main__":
    unittest.main()
