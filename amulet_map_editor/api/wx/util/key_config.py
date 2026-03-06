import wx
from wx.lib.wordwrap import wordwrap
from amulet_map_editor.api import lang
from amulet_map_editor.api.wx.ui.simple import (
    SimpleDialog,
    SimpleScrollablePanel,
    SimpleChoiceAny,
)
from typing import Dict, Tuple, Optional, Union, Sequence

from amulet_map_editor.api.image import ADD_ICON, SUBTRACT_ICON, EDIT_ICON

ModifierKeyType = str
KeyType = Union[int, str]
KeybindGroupIdType = str
KeyActionType = str
ModifierType = Tuple[ModifierKeyType, ...]
SerialisedKeyType = Tuple[ModifierType, KeyType]
KeybindGroup = Dict[KeyActionType, SerialisedKeyType]
ActionLookupType = Dict[SerialisedKeyType, KeyActionType]
KeybindContainer = Dict[KeybindGroupIdType, KeybindGroup]

PRESET_GROUP_LABELS: Dict[str, str] = {
    "right": "Right hand on Mouse",
    "left": "Left hand on Mouse",
}

PRESET_GROUP_LABELS_MOUSE: Dict[str, str] = {
    "right": "Left Mouse",
    "left": "Right Mouse",
}

MouseLeft = "MOUSE_LEFT"
MouseMiddle = "MOUSE_MIDDLE"
MouseRight = "MOUSE_RIGHT"
MouseAux1 = "MOUSE_AUX_1"
MouseAux2 = "MOUSE_AUX_2"
MouseWheelScrollUp = "MOUSE_WHEEL_SCROLL_UP"
MouseWheelScrollDown = "MOUSE_WHEEL_SCROLL_DOWN"
Control = "CTRL"
Shift = "SHIFT"
Alt = "ALT"

Space = "SPACE"
PageUp = "PAGE_UP"
PageDown = "PAGE_DOWN"
Back = "BACK"
Tab = "TAB"
Return = "RETURN"
Escape = "ESCAPE"
Delete = "DELETE"
Start = "START"
Menu = "MENU"
Pause = "PAUSE"
Capital = "CAPITAL"
End = "END"
Home = "HOME"
Left = "LEFT"
Up = "UP"
Right = "RIGHT"
Down = "DOWN"
Select = "SELECT"
Print = "PRINT"
Execute = "EXECUTE"
Snapshot = "SNAPSHOT"
Insert = "INSERT"
Help = "HELP"
Numpad0 = "NUMPAD0"
Numpad1 = "NUMPAD1"
Numpad2 = "NUMPAD2"
Numpad3 = "NUMPAD3"
Numpad4 = "NUMPAD4"
Numpad5 = "NUMPAD5"
Numpad6 = "NUMPAD6"
Numpad7 = "NUMPAD7"
Numpad8 = "NUMPAD8"
Numpad9 = "NUMPAD9"
Multiply = "MULTIPLY"
Add = "ADD"
Separator = "SEPARATOR"
Subtract = "SUBTRACT"
Decimal = "DECIMAL"
Divide = "DIVIDE"
F1 = "F1"
F2 = "F2"
F3 = "F3"
F4 = "F4"
F5 = "F5"
F6 = "F6"
F7 = "F7"
F8 = "F8"
F9 = "F9"
F10 = "F10"
F11 = "F11"
F12 = "F12"
F13 = "F13"
F14 = "F14"
F15 = "F15"
F16 = "F16"
F17 = "F17"
F18 = "F18"
F19 = "F19"
F20 = "F20"
F21 = "F21"
F22 = "F22"
F23 = "F23"
F24 = "F24"
Numlock = "NUMLOCK"
Scroll = "SCROLL"
Numpad_Space = "NUMPAD_SPACE"
Numpad_Tab = "NUMPAD_TAB"
Numpad_Enter = "NUMPAD_ENTER"
Numpad_F1 = "NUMPAD_F1"
Numpad_F2 = "NUMPAD_F2"
Numpad_F3 = "NUMPAD_F3"
Numpad_F4 = "NUMPAD_F4"
Numpad_Home = "NUMPAD_HOME"
Numpad_Left = "NUMPAD_LEFT"
Numpad_Up = "NUMPAD_UP"
Numpad_Right = "NUMPAD_RIGHT"
Numpad_Down = "NUMPAD_DOWN"
Numpad_Pageup = "NUMPAD_PAGEUP"
Numpad_Pagedown = "NUMPAD_PAGEDOWN"
Numpad_End = "NUMPAD_END"
Numpad_Begin = "NUMPAD_BEGIN"
Numpad_Insert = "NUMPAD_INSERT"
Numpad_Delete = "NUMPAD_DELETE"
Numpad_Equal = "NUMPAD_EQUAL"
Numpad_Multiply = "NUMPAD_MULTIPLY"
Numpad_Add = "NUMPAD_ADD"
Numpad_Separator = "NUMPAD_SEPARATOR"
Numpad_Subtract = "NUMPAD_SUBTRACT"
Numpad_Decimal = "NUMPAD_DECIMAL"
Numpad_Divide = "NUMPAD_DIVIDE"

key_string_map = {
    wx.WXK_CONTROL: Control,
    wx.WXK_SHIFT: Shift,
    wx.WXK_ALT: Alt,
    wx.WXK_SPACE: Space,
    wx.WXK_PAGEUP: PageUp,
    wx.WXK_PAGEDOWN: PageDown,
    wx.WXK_BACK: Back,
    wx.WXK_TAB: Tab,
    wx.WXK_RETURN: Return,
    wx.WXK_ESCAPE: Escape,
    wx.WXK_DELETE: Delete,
    wx.WXK_START: Start,
    wx.WXK_MENU: Menu,
    wx.WXK_PAUSE: Pause,
    wx.WXK_CAPITAL: Capital,
    wx.WXK_END: End,
    wx.WXK_HOME: Home,
    wx.WXK_LEFT: Left,
    wx.WXK_UP: Up,
    wx.WXK_RIGHT: Right,
    wx.WXK_DOWN: Down,
    wx.WXK_SELECT: Select,
    wx.WXK_PRINT: Print,
    wx.WXK_EXECUTE: Execute,
    wx.WXK_SNAPSHOT: Snapshot,
    wx.WXK_INSERT: Insert,
    wx.WXK_HELP: Help,
    wx.WXK_NUMPAD0: Numpad0,
    wx.WXK_NUMPAD1: Numpad1,
    wx.WXK_NUMPAD2: Numpad2,
    wx.WXK_NUMPAD3: Numpad3,
    wx.WXK_NUMPAD4: Numpad4,
    wx.WXK_NUMPAD5: Numpad5,
    wx.WXK_NUMPAD6: Numpad6,
    wx.WXK_NUMPAD7: Numpad7,
    wx.WXK_NUMPAD8: Numpad8,
    wx.WXK_NUMPAD9: Numpad9,
    wx.WXK_MULTIPLY: Multiply,
    wx.WXK_ADD: Add,
    wx.WXK_SEPARATOR: Separator,
    wx.WXK_SUBTRACT: Subtract,
    wx.WXK_DECIMAL: Decimal,
    wx.WXK_DIVIDE: Divide,
    wx.WXK_F1: F1,
    wx.WXK_F2: F2,
    wx.WXK_F3: F3,
    wx.WXK_F4: F4,
    wx.WXK_F5: F5,
    wx.WXK_F6: F6,
    wx.WXK_F7: F7,
    wx.WXK_F8: F8,
    wx.WXK_F9: F9,
    wx.WXK_F10: F10,
    wx.WXK_F11: F11,
    wx.WXK_F12: F12,
    wx.WXK_F13: F13,
    wx.WXK_F14: F14,
    wx.WXK_F15: F15,
    wx.WXK_F16: F16,
    wx.WXK_F17: F17,
    wx.WXK_F18: F18,
    wx.WXK_F19: F19,
    wx.WXK_F20: F20,
    wx.WXK_F21: F21,
    wx.WXK_F22: F22,
    wx.WXK_F23: F23,
    wx.WXK_F24: F24,
    wx.WXK_NUMLOCK: Numlock,
    wx.WXK_SCROLL: Scroll,
    wx.WXK_NUMPAD_SPACE: Numpad_Space,
    wx.WXK_NUMPAD_TAB: Numpad_Tab,
    wx.WXK_NUMPAD_ENTER: Numpad_Enter,
    wx.WXK_NUMPAD_F1: Numpad_F1,
    wx.WXK_NUMPAD_F2: Numpad_F2,
    wx.WXK_NUMPAD_F3: Numpad_F3,
    wx.WXK_NUMPAD_F4: Numpad_F4,
    wx.WXK_NUMPAD_HOME: Numpad_Home,
    wx.WXK_NUMPAD_LEFT: Numpad_Left,
    wx.WXK_NUMPAD_UP: Numpad_Up,
    wx.WXK_NUMPAD_RIGHT: Numpad_Right,
    wx.WXK_NUMPAD_DOWN: Numpad_Down,
    wx.WXK_NUMPAD_PAGEUP: Numpad_Pageup,
    wx.WXK_NUMPAD_PAGEDOWN: Numpad_Pagedown,
    wx.WXK_NUMPAD_END: Numpad_End,
    wx.WXK_NUMPAD_BEGIN: Numpad_Begin,
    wx.WXK_NUMPAD_INSERT: Numpad_Insert,
    wx.WXK_NUMPAD_DELETE: Numpad_Delete,
    wx.WXK_NUMPAD_EQUAL: Numpad_Equal,
    wx.WXK_NUMPAD_MULTIPLY: Numpad_Multiply,
    wx.WXK_NUMPAD_ADD: Numpad_Add,
    wx.WXK_NUMPAD_SEPARATOR: Numpad_Separator,
    wx.WXK_NUMPAD_SUBTRACT: Numpad_Subtract,
    wx.WXK_NUMPAD_DECIMAL: Numpad_Decimal,
    wx.WXK_NUMPAD_DIVIDE: Numpad_Divide,
}

_mouse_events = {
    wx.EVT_LEFT_DOWN.evtType[0]: MouseLeft,
    wx.EVT_LEFT_UP.evtType[0]: MouseLeft,
    wx.EVT_MIDDLE_DOWN.evtType[0]: MouseMiddle,
    wx.EVT_MIDDLE_UP.evtType[0]: MouseMiddle,
    wx.EVT_RIGHT_DOWN.evtType[0]: MouseRight,
    wx.EVT_RIGHT_UP.evtType[0]: MouseRight,
    wx.EVT_MOUSE_AUX1_DOWN.evtType[0]: MouseAux1,
    wx.EVT_MOUSE_AUX1_UP.evtType[0]: MouseAux1,
    wx.EVT_MOUSE_AUX2_DOWN.evtType[0]: MouseAux2,
    wx.EVT_MOUSE_AUX2_UP.evtType[0]: MouseAux2,
}


def serialise_modifier(
    evt: Union[wx.KeyEvent, wx.MouseEvent], key: int
) -> ModifierType:
    modifier = []
    if evt.ControlDown() and key != wx.WXK_CONTROL:
        modifier.append(Control)
    if evt.ShiftDown() and key != wx.WXK_SHIFT:
        modifier.append(Shift)
    if evt.AltDown() and key != wx.WXK_ALT:
        modifier.append(Alt)
    return tuple(modifier)


def serialise_key(evt: Union[wx.KeyEvent, wx.MouseEvent]) -> Optional[KeyType]:
    """Get the serialised version of the key that was pressed/released."""
    if isinstance(evt, wx.KeyEvent):
        key = evt.GetUnicodeKey() or evt.GetKeyCode()

        if 33 <= key <= 126:
            key = chr(key).upper()
        elif key in key_string_map:
            key = key_string_map[key]
        else:
            key = f"UNKNOWN KEY {key}"
        return key
    elif isinstance(evt, wx.MouseEvent):
        key = evt.GetEventType()
        if key in wx.EVT_MOUSEWHEEL.evtType:
            if evt.GetWheelRotation() < 0:
                return MouseWheelScrollDown
            elif evt.GetWheelRotation() > 0:
                return MouseWheelScrollUp
        elif key in _mouse_events:
            return _mouse_events[key]


def serialise_key_event(
    evt: Union[wx.KeyEvent, wx.MouseEvent],
) -> Optional[SerialisedKeyType]:
    if isinstance(evt, wx.KeyEvent):
        key = evt.GetUnicodeKey() or evt.GetKeyCode()
        if key in (wx.WXK_CONTROL, wx.WXK_SHIFT, wx.WXK_ALT):
            return
        modifier = serialise_modifier(evt, key)

        if 33 <= key <= 126:
            key = chr(key).upper()
        elif key in key_string_map:
            key = key_string_map[key]
        else:
            key = f"UNKNOWN KEY {key}"
        return modifier, key
    elif isinstance(evt, wx.MouseEvent):
        key = evt.GetEventType()
        modifier = serialise_modifier(evt, key)
        if key in wx.EVT_MOUSEWHEEL.evtType:
            if evt.GetWheelRotation() < 0:
                return modifier, MouseWheelScrollDown
            elif evt.GetWheelRotation() > 0:
                return modifier, MouseWheelScrollUp
        elif key in _mouse_events:
            return modifier, _mouse_events[key]


def stringify_key(key: SerialisedKeyType) -> str:
    return " + ".join([str(s) for s in key[0] + (key[1],)])


def format_key_display(key_text: str) -> str:
    return key_text.upper()


def format_label_display(label_text: str) -> str:
    stripped_text = label_text.replace("&&", "\0")
    stripped_text = stripped_text.replace("&", "")
    stripped_text = stripped_text.replace("\0", "&")
    text = stripped_text.strip()
    if not text:
        return text
    first_alpha_index = next((i for i, char in enumerate(text) if char.isalpha()), -1)
    if first_alpha_index == -1:
        return text
    return (
        text[:first_alpha_index]
        + text[first_alpha_index].upper()
        + text[first_alpha_index + 1 :].lower()
    )


class KeyCatcher(wx.Dialog):
    def __init__(self, parent: wx.Window, action: str):
        super().__init__(
            parent,
            title=lang.get("key_config.press_label").format(
                action=lang.get(f"action.{action.lower()}")
            ),
            style=wx.DEFAULT_DIALOG_STYLE | wx.WANTS_CHARS,
        )

        self._key = ((), "NONE")

        panel = wx.Panel(self)
        panel.SetFocus()

        panel.Bind(wx.EVT_LEFT_DOWN, self._on_key)
        panel.Bind(wx.EVT_MIDDLE_DOWN, self._on_key)
        panel.Bind(wx.EVT_RIGHT_DOWN, self._on_key)
        panel.Bind(wx.EVT_KEY_DOWN, self._on_key)
        panel.Bind(wx.EVT_MOUSEWHEEL, self._on_key)
        panel.Bind(wx.EVT_MOUSE_AUX1_DOWN, self._on_key)
        panel.Bind(wx.EVT_MOUSE_AUX2_DOWN, self._on_key)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.Layout()

    def _on_key(self, evt):
        key = serialise_key_event(evt)
        if key is not None:
            self._key = key
            self.EndModal(1)

    @property
    def key(self) -> SerialisedKeyType:
        return self._key


# TODO: make any key able to be a modifier. Instead of registering keys on press register them on release.
#  When a key is pressed store it to a set of persistent keys. When a key is released that is the triggering
#  key and all persistent keys are modifiers.
#  In the actual program detect all keys on press/release as normal but also store the set of persistent keys.
#  When serialising give the key that was pressed/released along with all the modifiers.
#  Return all actions that use the triggering key as the triggering key and use a sub-set of the persistent keys.


class KeyConfigDialog(SimpleDialog):
    def __init__(
        self,
        parent: wx.Window,
        selected_group: KeybindGroupIdType,
        entries: Sequence[KeyActionType],
        fixed_keybinds: KeybindContainer,
        user_keybinds: KeybindContainer,
        action_groups: Optional[Dict[str, Sequence[KeyActionType]]] = None,
        show_misc: bool = True,
        show_descriptions: bool = True,
        require_mouse_action: Optional[bool] = None,
    ):
        # Initialize SimpleDialog but override the style to include window management
        wx.Dialog.__init__(
            self,
            parent,
            title=lang.get("key_config.key_select"),
            style=wx.CAPTION
            | wx.CLOSE_BOX
            | wx.MAXIMIZE_BOX
            | wx.MINIMIZE_BOX
            | wx.SYSTEM_MENU
            | wx.RESIZE_BORDER,
        )
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.sizer, 1, wx.EXPAND)
        self.bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.bottom_sizer, 0, wx.EXPAND)
        self.bottom_sizer.AddStretchSpacer()
        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL)
        self.bottom_sizer.Add(button_sizer, flag=wx.ALL, border=5)
        
        self._key_config = KeyConfig(
            self, selected_group, entries, fixed_keybinds, user_keybinds, action_groups, show_misc, show_descriptions, require_mouse_action
        )
        self.sizer.Add(self._key_config, 1, wx.EXPAND)
        self.Layout()
        self.Fit()
        width, height = self.GetSize()
        self.SetMinSize((max(1080, width), max(700, height)))
        
        # Set focus on the scrollable panel for keyboard navigation
        wx.CallAfter(self._key_config._options.SetFocus)

    @property
    def options(self) -> Tuple[KeybindContainer, KeybindGroupIdType, KeybindGroup]:
        return self._key_config.options


class KeyConfig(wx.BoxSizer):
    _EDITABLE_KEY_BUTTON_MIN_WIDTH = 240

    def __init__(
        self,
        parent: wx.Window,
        selected_group: KeybindGroupIdType,
        entries: Sequence[KeyActionType],
        fixed_keybinds: KeybindContainer,
        user_keybinds: KeybindContainer,
        action_groups: Optional[Dict[str, Sequence[KeyActionType]]] = None,
        show_misc: bool = True,
        show_descriptions: bool = True,
        require_mouse_action: Optional[bool] = None,
    ):
        super().__init__(wx.VERTICAL)
        self._entries = entries
        self._fixed_keybinds = fixed_keybinds
        self._user_keybinds = user_keybinds
        self._action_groups = action_groups
        self._show_misc = show_misc
        self._show_descriptions = show_descriptions
        self._require_mouse_action = require_mouse_action

        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.Add(top_sizer, 0, wx.EXPAND)
        self._choice = SimpleChoiceAny(parent, sort=False)
        self._choice.SetItems(self._choice_items(), selected_group)
        self._choice.Bind(wx.EVT_CHOICE, self._on_group_change)
        top_sizer.Add(self._choice, 1, wx.ALL | wx.EXPAND, 5)

        add = wx.BitmapButton(parent, bitmap=ADD_ICON.bitmap(32, 32))
        add.Bind(wx.EVT_BUTTON, lambda evt: self._create_new_group())
        top_sizer.Add(add, 0, wx.ALL, 5)

        self._delete = wx.BitmapButton(parent, bitmap=SUBTRACT_ICON.bitmap(32, 32))
        self._delete.Bind(wx.EVT_BUTTON, lambda evt: self._delete_group())
        top_sizer.Add(self._delete, 0, wx.ALL, 5)

        self._rename = wx.BitmapButton(parent, bitmap=EDIT_ICON.bitmap(32, 32))
        self._rename.SetToolTip("Edit Name")
        self._rename.Bind(wx.EVT_BUTTON, lambda evt: self._rename_group())
        top_sizer.Add(self._rename, 0, wx.ALL, 5)

        self._options = SimpleScrollablePanel(parent, size=(760, 560))
        self.Add(self._options, 1, wx.EXPAND)

        self._key_buttons: Dict[str, wx.Button] = {}
        self._rebuild_buttons()

    def _rebuild_buttons(self):
        group_id = self._current_group_id()
        if group_id in self._fixed_keybinds:
            group = self._fixed_keybinds[group_id]
            self._delete.Disable()
            self._rename.Disable()
            editable = False
        else:
            group = self._user_keybinds[group_id]
            self._delete.Enable()
            self._rename.Enable()
            editable = True

        # Rebuild the options panel with or without grouping
        if self._action_groups:
            self._rebuild_grouped_options(group, editable)
        else:
            self._rebuild_ungrouped_options(group, editable)

    def _choice_items(self) -> Dict[str, str]:
        items: Dict[str, str] = {}
        preset_labels = (
            PRESET_GROUP_LABELS_MOUSE
            if self._require_mouse_action is True
            else PRESET_GROUP_LABELS
        )
        for group_id in self._fixed_keybinds.keys():
            items[group_id] = preset_labels.get(group_id, group_id)
        for group_id in self._user_keybinds.keys():
            items[group_id] = group_id
        return items

    def _current_group_id(self) -> str:
        group_id = self._choice.GetCurrentObject()
        if isinstance(group_id, str):
            return group_id
        return self._choice.GetCurrentString()

    def _create_selectable_text(
        self, text: str, bold: bool = False, min_width: int = 0
    ) -> wx.TextCtrl:
        ctrl = wx.TextCtrl(
            self._options,
            value=text,
            style=wx.TE_READONLY | wx.BORDER_NONE,
        )
        ctrl.SetBackgroundColour(self._options.GetBackgroundColour())
        if min_width > 0:
            ctrl.SetMinSize((min_width, -1))
        if bold:
            font = ctrl.GetFont()
            ctrl.SetFont(font.Bold())
        ctrl.Bind(wx.EVT_MOUSEWHEEL, self._on_selectable_text_mouse_wheel)
        return ctrl

    def _create_selectable_paragraph(
        self, text: str, wrap_width: int, italic: bool = False
    ) -> wx.TextCtrl:
        ctrl = wx.TextCtrl(
            self._options,
            value="",
            style=wx.TE_READONLY | wx.TE_MULTILINE | wx.BORDER_NONE,
        )
        ctrl.SetBackgroundColour(self._options.GetBackgroundColour())
        font = ctrl.GetFont()
        if italic:
            font.SetStyle(wx.FONTSTYLE_ITALIC)
        ctrl.SetFont(font)

        dc = wx.ClientDC(self._options)
        dc.SetFont(ctrl.GetFont())
        wrapped_text = wordwrap(text, wrap_width, dc)
        ctrl.SetValue(wrapped_text)

        line_count = max(1, wrapped_text.count("\n") + 1)
        height = ctrl.GetCharHeight() * line_count + 8
        ctrl.SetMinSize((wrap_width + 10, height))
        ctrl.Bind(wx.EVT_MOUSEWHEEL, self._on_selectable_text_mouse_wheel)
        return ctrl

    def _on_selectable_text_mouse_wheel(self, evt: wx.MouseEvent):
        wheel_delta = evt.GetWheelDelta() or 120
        wheel_rotation = evt.GetWheelRotation()
        lines_per_action = evt.GetLinesPerAction() or 3
        if wheel_rotation != 0 and hasattr(self._options, "ScrollLines"):
            scroll_lines = -int(wheel_rotation / wheel_delta) * lines_per_action
            if scroll_lines != 0:
                self._options.ScrollLines(scroll_lines)

    def _refresh_options_scroll(self):
        self._options.Layout()
        self._options.FitInside()

    def _rebuild_grouped_options(self, group, editable: bool):
        """Rebuild options panel with section headings and grouped actions."""
        # Clear existing widgets
        self._options.sizer.Clear(True)
        self._key_buttons.clear()
        
        # Create main vertical sizer
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self._options.sizer.Add(main_sizer, 1, wx.EXPAND | wx.ALL, 5)

        if self._show_misc:
            philosophy_text = lang.get("key_config.philosophy")
            philosophy_label = self._create_selectable_paragraph(
                philosophy_text, wrap_width=620
            )
            main_sizer.Add(philosophy_label, 0, wx.ALL | wx.EXPAND, 10)
            main_sizer.Add(wx.StaticLine(self._options), 0, wx.EXPAND | wx.ALL, 5)

        if self._show_misc:
            self._add_misc_hotkeys(main_sizer, group)
            main_sizer.Add(wx.StaticLine(self._options), 0, wx.EXPAND | wx.ALL, 5)
        
        # Iterate through groups and add sections
        for group_name, actions in self._action_groups.items():
            # Filter to only show actions that exist in entries
            actions_to_show = [a for a in actions if a in self._entries]
            readonly_items = self._get_group_readonly_items(group_name, group)
            
            # Add group heading (show all groups, even if empty)
            heading_key = f"key_config.group_name.{group_name}"
            heading_text = lang.get(heading_key)
            if heading_text == heading_key:
                heading_text = group_name.replace("_", " ").title()
            heading = wx.StaticText(self._options, label=heading_text)
            font = heading.GetFont()
            font.PointSize += 2
            font = font.Bold()
            heading.SetFont(font)
            main_sizer.Add(heading, 0, wx.ALL, 5)
            
            # Try to add group description if it exists
            description_key = f"key_config.group_description.{group_name}"
            description_text = lang.get(description_key)
            if self._show_descriptions and description_text != description_key:  # If not the key itself, we have a valid translation
                description = self._create_selectable_paragraph(
                    description_text, wrap_width=500, italic=True
                )
                main_sizer.Add(description, 0, wx.ALL | wx.EXPAND, 5)
            
            # Add grid for this group if it has actions
            if actions_to_show or readonly_items:
                grid_sizer = wx.FlexGridSizer(0, 2, 5, 5)
                grid_sizer.AddGrowableCol(1, 1)
                readonly_added = False

                for action in actions_to_show:
                    key_text = format_key_display(
                        stringify_key(group.get(action, ((), "NONE")))
                    )
                    if editable:
                        self._key_buttons[action] = button = wx.Button(self._options)
                        button.SetLabel(key_text)
                        button.SetMinSize((self._EDITABLE_KEY_BUTTON_MIN_WIDTH, -1))
                        button.Bind(
                            wx.EVT_BUTTON,
                            lambda evt, a=action: self._modify_button(a),
                        )
                        grid_sizer.Add(
                            button,
                            0,
                            wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT,
                            12,
                        )
                    else:
                        hotkey_label = self._create_selectable_text(
                            key_text,
                            bold=True,
                            min_width=180,
                        )
                        grid_sizer.Add(
                            hotkey_label,
                            0,
                            wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT,
                            12,
                        )
                    label = self._create_selectable_text(
                        format_label_display(lang.get(f"action.{action.lower()}")),
                        min_width=420,
                    )
                    grid_sizer.Add(
                        label,
                        0,
                        wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT,
                        12,
                    )

                    if group_name == "navigation" and action == "ACT_TOGGLE_WASD_MODE":
                        for label_text, hotkey_text in readonly_items:
                            hotkey_label = self._create_selectable_text(
                                format_key_display(hotkey_text),
                                bold=True,
                                min_width=180,
                            )
                            grid_sizer.Add(
                                hotkey_label,
                                0,
                                wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT,
                                12,
                            )
                            readonly_label = self._create_selectable_text(
                                format_label_display(label_text),
                                min_width=420,
                            )
                            grid_sizer.Add(
                                readonly_label,
                                0,
                                wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT,
                                12,
                            )
                        readonly_added = True

                if not readonly_added:
                    for label_text, hotkey_text in readonly_items:
                        hotkey_align = (
                            wx.ALIGN_LEFT if group_name == "select_mode" else wx.ALIGN_RIGHT
                        )
                        hotkey_label = self._create_selectable_text(
                            format_key_display(hotkey_text),
                            bold=True,
                            min_width=180,
                        )
                        grid_sizer.Add(
                            hotkey_label,
                            0,
                            hotkey_align | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT,
                            12,
                        )
                        readonly_label = self._create_selectable_text(
                            format_label_display(label_text),
                            min_width=420,
                        )
                        grid_sizer.Add(
                            readonly_label,
                            0,
                            wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT,
                            12,
                        )
                
                main_sizer.Add(grid_sizer, 0, wx.ALL | wx.EXPAND, 5)
            else:
                # Show "No actions" text for empty groups
                empty_label = wx.StaticText(self._options, label="(no actions)")
                empty_label_font = empty_label.GetFont()
                empty_label_font.SetStyle(wx.FONTSTYLE_ITALIC)
                empty_label.SetFont(empty_label_font)
                main_sizer.Add(empty_label, 0, wx.ALL, 5)
            
            # Add spacing between groups
            main_sizer.Add(wx.StaticLine(self._options), 0, wx.EXPAND | wx.ALL, 5)
        
        self._refresh_options_scroll()

    def _get_group_readonly_items(self, group_name: str, group: KeybindGroup):
        if group_name == "navigation":
            return [
                (lang.get("program_3d_edit.menu_bar.navigation.goto"), "Ctrl+G"),
            ]
        elif group_name == "select_mode":
            return [
                (lang.get("program_3d_edit.menu_bar.edit.cut"), "Ctrl+X"),
                (lang.get("program_3d_edit.menu_bar.edit.copy"), "Ctrl+C"),
                (lang.get("program_3d_edit.select_tool.delete_button"), "Delete"),
            ]
        return []

    def _add_misc_hotkeys(self, main_sizer: wx.BoxSizer, group: KeybindGroup):
        heading = wx.StaticText(self._options, label="Common")
        font = heading.GetFont()
        font.PointSize += 2
        font = font.Bold()
        heading.SetFont(font)

        misc_hotkeys = [
            (lang.get("menu_bar.file.open_world"), "Ctrl+O", None),
            ("Close World / Quit", "Ctrl+Q", None),
            ("Quit Without Saving", "Ctrl+Alt+Shift+Q", "ACT_QUIT_WITHOUT_SAVE"),
            (lang.get("program_3d_edit.menu_bar.file.save"), "Ctrl+S", None),
            ("Save All", "Ctrl+Shift+S", "ACT_SAVE_ALL"),
            ("Save All and Quit", "Ctrl+Shift+Q", "ACT_SAVE_ALL_CLOSE"),
            ("Next Tab in Current World", "Ctrl+Shift+Page Down", None),
            ("Previous Tab in Current World", "Ctrl+Shift+Page Up", None),
            ("Next World", "Ctrl+Page Down", None),
            ("Previous World", "Ctrl+Page Up", None),
            (lang.get("program_3d_edit.menu_bar.file.preferences"), "Ctrl+P", None),
            (lang.get("program_3d_edit.menu_bar.options.keyboard_controls"), "Ctrl+K", None),
            (lang.get("program_3d_edit.menu_bar.options.mouse_control"), "Ctrl+M", None),
            (lang.get("program_3d_edit.menu_bar.options.camera"), "Ctrl+I", None),
            (lang.get("program_3d_edit.menu_bar.edit.undo"), "Ctrl+Z", None),
            (lang.get("program_3d_edit.menu_bar.edit.redo"), "Ctrl+Y", None),
            (lang.get("program_3d_edit.menu_bar.edit.paste"), "Ctrl+V", "ACT_PASTE"),
            (lang.get("program_3d_edit.menu_bar.edit.select_all"), "Ctrl+A", None),
        ]

        grid_sizer = wx.FlexGridSizer(len(misc_hotkeys), 2, 5, 10)
        grid_sizer.AddGrowableCol(1, 1)
        for label, fallback_hotkey, action_id in misc_hotkeys:
            # Strip ellipsis (...) from menu labels in this static display
            display_label = label.replace("...", "")
            hotkey = self._group_hotkey(group, action_id, fallback_hotkey)
            hotkey_label = self._create_selectable_text(
                format_key_display(hotkey),
                bold=True,
                min_width=180,
            )
            grid_sizer.Add(
                hotkey_label,
                0,
                wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT,
                12,
            )
            label_text = self._create_selectable_text(
                format_label_display(display_label),
                min_width=420,
            )
            grid_sizer.Add(
                label_text,
                0,
                wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT,
                12,
            )

        main_sizer.Add(heading, 0, wx.LEFT | wx.BOTTOM, 5)
        main_sizer.Add(grid_sizer, 0, wx.ALL, 5)

    def _group_hotkey(
        self,
        group: KeybindGroup,
        action_id: Optional[str],
        fallback_hotkey: str,
    ) -> str:
        if action_id is not None and action_id in group:
            return stringify_key(group[action_id]).replace(" + ", "+")
        return fallback_hotkey

    def _rebuild_ungrouped_options(self, group, editable: bool):
        """Rebuild options panel without grouping (original behavior)."""
        # Clear existing widgets
        self._options.sizer.Clear(True)
        self._key_buttons.clear()
        
        grid_sizer = wx.FlexGridSizer(len(self._entries), 2, 5, 5)
        grid_sizer.AddGrowableCol(1, 1)
        self._options.sizer.Add(grid_sizer, 0, wx.ALL | wx.EXPAND, 5)
        for action in self._entries:
            key_text = format_key_display(stringify_key(group.get(action, ((), "NONE"))))
            if editable:
                self._key_buttons[action] = button = wx.Button(self._options)
                button.SetLabel(key_text)
                button.SetMinSize((self._EDITABLE_KEY_BUTTON_MIN_WIDTH, -1))
                button.Bind(wx.EVT_BUTTON, lambda evt, a=action: self._modify_button(a))
                grid_sizer.Add(
                    button,
                    0,
                    wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT,
                    12,
                )
            else:
                hotkey_label = self._create_selectable_text(
                    key_text,
                    bold=True,
                    min_width=180,
                )
                grid_sizer.Add(
                    hotkey_label,
                    0,
                    wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL | wx.RIGHT,
                    12,
                )
            label = self._create_selectable_text(
                format_label_display(lang.get(f"action.{action.lower()}")),
                min_width=420,
            )
            grid_sizer.Add(
                label,
                0,
                wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL | wx.LEFT,
                12,
            )
        
        self._refresh_options_scroll()


    def _rebuild_choice(self, group_name=None):
        index = self._choice.GetSelection()
        self._choice.SetItems(self._choice_items(), group_name)
        if group_name is not None:
            pass
        else:
            self._choice.SetSelection(max(index - 1, 0))
        self._rebuild_buttons()

    def _delete_group(self):
        group = self._current_group_id()
        if group in self._user_keybinds:
            del self._user_keybinds[group]
            self._rebuild_choice()

    def _request_group_name(self) -> Optional[str]:
        group_name = ""
        while group_name == "":
            msg = wx.TextEntryDialog(
                self._options, lang.get("key_config.enter_group_name")
            )
            if msg.ShowModal() == wx.ID_OK:
                group_name = msg.GetValue()
                if (
                    group_name in self._fixed_keybinds
                    or group_name in self._user_keybinds
                ):
                    group_name = ""
            else:
                return
        return group_name

    def _rename_group(self):
        old_group_name = self._current_group_id()
        if old_group_name in self._user_keybinds:
            group_name = self._request_group_name()
            if group_name is None:
                return
            group = self._user_keybinds[old_group_name]
            del self._user_keybinds[old_group_name]
            self._user_keybinds[group_name] = group
            self._rebuild_choice(group_name)

    def _create_new_group(self):
        group_name = self._request_group_name()
        if group_name is None:
            return
        old_group_name = self._current_group_id()
        if old_group_name in self._fixed_keybinds:
            group = self._fixed_keybinds[old_group_name]
        else:
            group = self._user_keybinds[old_group_name]
        new_group = group.copy()

        # Safeguard: when cloning a user-defined group, backfill any missing
        # mappings from a fixed preset so partial groups stay complete.
        if old_group_name in self._user_keybinds and self._fixed_keybinds:
            fallback_fixed_group = self._fixed_keybinds.get(old_group_name)
            if fallback_fixed_group is None:
                first_fixed_group_id = next(iter(self._fixed_keybinds))
                fallback_fixed_group = self._fixed_keybinds[first_fixed_group_id]
            for action, key in fallback_fixed_group.items():
                new_group.setdefault(action, key)

        self._user_keybinds[group_name] = new_group
        self._rebuild_choice(group_name)

    def _is_mouse_key(self, key: SerialisedKeyType) -> bool:
        """Check if a key binding includes a mouse action."""
        _, key_value = key
        mouse_keys = {
            MouseLeft, MouseMiddle, MouseRight,
            MouseAux1, MouseAux2,
            MouseWheelScrollUp, MouseWheelScrollDown
        }
        return key_value in mouse_keys

    def _modify_button(self, action):
        if self._current_group_id() in self._fixed_keybinds:
            msg = wx.MessageDialog(
                self._options,
                lang.get("key_config.active_not_editable"),
                style=wx.YES_NO,
            )
            if msg.ShowModal() == wx.ID_YES:
                self._create_new_group()
            else:
                return
        group_name = self._current_group_id()
        if group_name in self._user_keybinds:
            while True:
                catcher = KeyCatcher(self._options, action)
                catcher.ShowModal()
                key = catcher.key
                
                # Validate the key based on mode
                is_mouse = self._is_mouse_key(key)
                if self._require_mouse_action is False and is_mouse:
                    # Keyboard controls: mouse actions not allowed
                    msg = wx.MessageDialog(
                        self._options,
                        "Keyboard controls cannot use mouse buttons or wheel.\nPlease press a keyboard key.",
                        "Invalid Key",
                        style=wx.OK | wx.ICON_ERROR,
                    )
                    msg.ShowModal()
                    continue
                elif self._require_mouse_action is True and not is_mouse:
                    # Mouse controls: must include mouse action
                    msg = wx.MessageDialog(
                        self._options,
                        "Mouse controls must include a mouse button or wheel action.\n(Keyboard modifiers like Ctrl, Shift, Alt are optional)",
                        "Invalid Key",
                        style=wx.OK | wx.ICON_ERROR,
                    )
                    msg.ShowModal()
                    continue
                
                # Key is valid
                self._user_keybinds[group_name][action] = key
                self._rebuild_buttons()
                break

    def _on_group_change(self, evt):
        self._rebuild_buttons()

    @property
    def options(self) -> Tuple[KeybindContainer, KeybindGroupIdType, KeybindGroup]:
        keybind_group = self._current_group_id()
        if keybind_group in self._fixed_keybinds:
            keybinds = self._fixed_keybinds[keybind_group]
        else:
            keybinds = self._user_keybinds[keybind_group]
        return self._user_keybinds, keybind_group, keybinds
