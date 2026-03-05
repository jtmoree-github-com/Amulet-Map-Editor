import unittest

from amulet.api.selection import SelectionBox, SelectionGroup
from amulet_map_editor.programs.edit.plugins.tools.select import SelectTool


class _DummySelection:
    def __init__(self):
        self._active_block_positions = ((0, 0, 0), (1, 1, 1))
        self.selection_group = SelectionGroup(
            [
                SelectionBox((0, 0, 0), (2, 2, 2)),
                SelectionBox((10, 10, 10), (12, 12, 12)),
            ]
        )

    @property
    def active_block_positions(self):
        return self._active_block_positions

    @active_block_positions.setter
    def active_block_positions(self, value):
        self._active_block_positions = value


class SelectToolMovementTestCase(unittest.TestCase):
    def setUp(self):
        self.tool = SelectTool.__new__(SelectTool)
        self.tool._selection = _DummySelection()

    def test_move_point1_only_updates_active_point1(self):
        before_group = self.tool._selection.selection_group

        self.tool._move_point1((3, -2, 5))

        self.assertEqual(((3, -2, 5), (1, 1, 1)), self.tool._selection.active_block_positions)
        self.assertEqual(before_group, self.tool._selection.selection_group)

    def test_move_point2_only_updates_active_point2(self):
        before_group = self.tool._selection.selection_group

        self.tool._move_point2((-4, 7, 2))

        self.assertEqual(((0, 0, 0), (-3, 8, 3)), self.tool._selection.active_block_positions)
        self.assertEqual(before_group, self.tool._selection.selection_group)


if __name__ == "__main__":
    unittest.main()
