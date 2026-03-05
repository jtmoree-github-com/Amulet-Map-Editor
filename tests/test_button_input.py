import unittest

from amulet_map_editor.api.wx.util.button_input import ButtonInput, Control


class ButtonInputMatchingTestCase(unittest.TestCase):
    def setUp(self):
        self.button_input = ButtonInput.__new__(ButtonInput)
        self.button_input._registered_actions = {}
        self.button_input._pressed_keys = set()
        self.button_input._continuous_actions = set()

    def test_ctrl_mouseleft_triggers_base_and_modified_action(self):
        self.button_input.register_action("ACT_BOX_CLICK", tuple(), "MOUSE_LEFT")
        self.button_input.register_action(
            "ACT_BOX_CLICK_ADD", (Control,), "MOUSE_LEFT"
        )

        self.button_input._pressed_keys.add(Control)
        actions = set(self.button_input._find_actions("MOUSE_LEFT"))

        self.assertIn("ACT_BOX_CLICK", actions)
        self.assertIn("ACT_BOX_CLICK_ADD", actions)

    def test_mouseleft_without_ctrl_only_triggers_base_action(self):
        self.button_input.register_action("ACT_BOX_CLICK", tuple(), "MOUSE_LEFT")
        self.button_input.register_action(
            "ACT_BOX_CLICK_ADD", (Control,), "MOUSE_LEFT"
        )

        actions = set(self.button_input._find_actions("MOUSE_LEFT"))

        self.assertIn("ACT_BOX_CLICK", actions)
        self.assertNotIn("ACT_BOX_CLICK_ADD", actions)

    def test_action_can_have_mouse_and_keyboard_triggers(self):
        self.button_input.register_action("ACT_BOX_CLICK", tuple(), "MOUSE_LEFT")
        self.button_input.register_action("ACT_BOX_CLICK", tuple(), "RETURN")

        keyboard_actions = set(self.button_input._find_actions("RETURN"))
        mouse_actions = set(self.button_input._find_actions("MOUSE_LEFT"))

        self.assertEqual({"ACT_BOX_CLICK"}, keyboard_actions)
        self.assertEqual({"ACT_BOX_CLICK"}, mouse_actions)


if __name__ == "__main__":
    unittest.main()