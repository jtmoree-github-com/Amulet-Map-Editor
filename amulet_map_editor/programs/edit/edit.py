from typing import TYPE_CHECKING, Optional, Generator
import webbrowser
import logging
from threading import Thread
import traceback

import wx

from amulet.api.data_types import OperationYieldType

EDIT_CONFIG_ID = "amulet_edit"
DEFAULT_RECENT_WORLDS_LIMIT = 5

from amulet_map_editor import lang
from amulet_map_editor.api.framework.programs import BaseProgram
from amulet_map_editor.api.framework.menu_utils import ensure_mnemonic
from amulet_map_editor.api.datatypes import MenuData
from amulet_map_editor.api.wx.util.key_config import KeyConfigDialog, KeyConfig
from amulet_map_editor.api.wx.ui.traceback_dialog import TracebackDialog
from amulet_map_editor.api.wx.ui.simple import SimpleDialog
from amulet_map_editor.programs.edit.api.canvas.edit_canvas import EditCanvas
from amulet_map_editor.programs.edit.api.key_config import (
    DefaultKeybindGroupId,
    PresetKeybinds,
    KeybindKeys,
    ActionGroups,
    KeyboardKeys,
    KeyboardPresets,
    KeyboardActionGroups,
    MouseKeys,
    MousePresets,
    MouseActionGroups,
    ACT_INCR_SPEED,
    ACT_DECR_SPEED,
    ACT_ZOOM_IN,
    ACT_ZOOM_OUT,
    ACT_SAVE_AS,
    ACT_SAVE_ALL,
    ACT_SAVE_ALL_CLOSE,
    ACT_QUIT_WITHOUT_SAVE,
    ACT_PASTE,
    ACT_DESELECT_BOX,
    ACT_DESELECT_ALL_BOXES,
    ACT_CHANGE_PROJECTION,
    ACT_TOGGLE_WASD_MODE,
    ACT_MOVE_CAMERA_TO_CURSOR,
    ACT_TELEPORT_CURSOR_TO_CAMERA,
    ACT_HELP,
    DOT,
    COMMA,
)
from amulet_map_editor.api import config, image
from amulet_map_editor.api.opengl.mesh.selection.box.colours import colours as selection_colours
from amulet_map_editor import close_level

if TYPE_CHECKING:
    from amulet.api.level import World

log = logging.getLogger(__name__)

_BOX_COLOUR_KEYS = {
    "mouse_cursor": "box_pointer",
    "clipboard_static": ("box_clip_static", "box_paste_static"),
    "point1": "box_point1",
    "point2": "box_point2",
    "moving_object": ("box_clipboard", "box_highlight_move"),
    "edge": "box_edge",
    "corner": "box_corner",
}

_BOX_COLOUR_DEFAULTS = {
    "mouse_cursor": tuple(selection_colours.get("box_pointer", selection_colours.get("box_normal", (1.0, 1.0, 1.0)))),
    "clipboard_static": tuple(selection_colours.get("box_clip_static", selection_colours.get("box_paste_static", (1.0, 1.0, 1.0)))),
    "point1": tuple(selection_colours.get("box_point1", (0.0, 1.0, 0.0))),
    "point2": tuple(selection_colours.get("box_point2", (1.0, 0.5, 0.85))),
    "moving_object": tuple(selection_colours.get("box_clipboard", selection_colours.get("box_highlight_move", (1.0, 0.7, 0.3)))),
    "edge": tuple(selection_colours.get("box_edge", (0.5, 1.0, 1.0))),
    "corner": tuple(selection_colours.get("box_corner", (1.0, 1.0, 0.5))),
}


class EditExtension(wx.Panel, BaseProgram):
    # UI elements
    _sizer: wx.BoxSizer
    # these only exists on setup. Once setup is finished they will be None
    _temp_msg: Optional[wx.StaticText]
    _temp_loading_bar: Optional[wx.Gauge]

    _world: "World"
    _canvas: Optional[EditCanvas]

    # setup is run in a different thread to avoid blocking the UI
    _setup_thread: Optional[Thread]

    def __init__(self, parent, world: "World"):
        wx.Panel.__init__(self, parent)
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        r, g, b = (int(v * 255) for v in EditCanvas.background_colour)
        self.SetBackgroundColour(wx.Colour(r, g, b))
        self.SetSizer(self._sizer)
        self._world = world
        self._canvas = None
        self._setup_thread = None
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

        self._sizer.AddStretchSpacer(1)
        self._temp_msg = wx.StaticText(
            self, label=lang.get("program_3d_edit.canvas.please_wait")
        )
        self._temp_msg.SetFont(wx.Font(40, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        self._sizer.Add(self._temp_msg, 0, flag=wx.ALIGN_CENTER_HORIZONTAL)
        self._temp_loading_bar = wx.Gauge(self, range=10000)
        self._sizer.Add(self._temp_loading_bar, 0, flag=wx.EXPAND)
        self._sizer.AddStretchSpacer(1)

    def enable(self):
        if self._canvas is None:
            self._canvas = EditCanvas(self, self._world)
            self._canvas.Hide()
            self._setup_thread = Thread(target=self._thread_setup)
            self._setup_thread.start()
        else:
            self._canvas.enable()

    def _update_loading(self, it: Generator[OperationYieldType, None, None]):
        for arg in it:
            if isinstance(arg, (int, float)):
                self._temp_loading_bar.SetValue(int(min(arg, 1) * 10000))
            elif (
                isinstance(arg, tuple)
                and isinstance(arg[0], (int, float))
                and isinstance(arg[1], str)
            ):
                self._temp_loading_bar.SetValue(int(min(arg[0], 1) * 10000))
                self._temp_msg.SetLabel(arg[1])
            self.Layout()

    def _display_error(self, msg, tb):
        dialog = TracebackDialog(
            self,
            "Exception while setting up canvas",
            msg,
            tb,
        )
        dialog.ShowModal()
        dialog.Destroy()
        self.Destroy()

    def _thread_setup(self):
        """
        Setup and enable all the UI elements.
        This can take a while to run so should be done in a new thread.
        Everything in here must be thread safe.
        """
        try:
            self._update_loading(self._canvas.thread_setup())
        except Exception as e:
            wx.CallAfter(self._display_error, str(e), traceback.format_exc())
            raise e
        else:
            wx.CallAfter(self._post_thread_setup)

    def _post_thread_setup(self):
        """
        Run any setup that is not thread safe.
        """
        try:
            self._update_loading(self._canvas.post_thread_setup())
            edit_config: dict = config.get(EDIT_CONFIG_ID, {})
            self._canvas.camera.perspective_fov = edit_config.get("options", {}).get(
                "fov", 70.0
            )
            if self._canvas.camera.perspective_fov > 180:
                self._canvas.camera.perspective_fov = 70.0
            self._canvas.renderer.render_distance = edit_config.get("options", {}).get(
                "render_distance", 5
            )
            self._canvas.camera.rotate_speed = edit_config.get("options", {}).get(
                "camera_sensitivity", 2.0
            )
            self._apply_box_colour_preferences(edit_config.get("options", {}))

            self._temp_msg = None
            self._temp_loading_bar = None
            self._sizer.Clear(True)
            self._sizer.Add(self._canvas, 1, wx.EXPAND)
            self._canvas.Show()
            self.Layout()
            # This must be called after the show handler is run
            wx.CallAfter(self._canvas.enable)
            # Give the canvas focus so keyboard shortcuts work immediately
            wx.CallAfter(self._canvas.SetFocus)
            self._setup_thread = None
        except Exception as e:
            wx.CallAfter(self._display_error, str(e), traceback.format_exc())
            raise e

    @staticmethod
    def _colour_pref_to_float(pref_value, default):
        if (
            isinstance(pref_value, (list, tuple))
            and len(pref_value) == 3
            and all(isinstance(v, (int, float)) for v in pref_value)
        ):
            if all(0 <= v <= 1 for v in pref_value):
                return tuple(float(v) for v in pref_value)
            if all(0 <= v <= 255 for v in pref_value):
                return tuple(float(v) / 255.0 for v in pref_value)
        return default

    def _apply_box_colour_preferences(self, options: dict):
        box_colours = options.get("box_colours", {}) if isinstance(options, dict) else {}
        for pref_key, colour_keys in _BOX_COLOUR_KEYS.items():
            default_colour = _BOX_COLOUR_DEFAULTS[pref_key]
            pref_value = box_colours.get(pref_key)
            if pref_key == "moving_object" and pref_value is None:
                pref_value = box_colours.get("clipboard")

            colour = self._colour_pref_to_float(pref_value, default_colour)
            if isinstance(colour_keys, str):
                colour_keys = (colour_keys,)
            for colour_key in colour_keys:
                selection_colours[colour_key] = colour

    def can_disable(self) -> bool:
        return self._setup_thread is None

    def disable(self):
        if self._canvas is not None:
            self._canvas.disable()

    def close(self):
        """Fully close the UI. Called when destroying the UI."""
        if self._canvas is not None:
            self._canvas.close()

    def can_close(self) -> bool:
        """
        Check if it is safe to close the UI.
        :return: True if the program can be closed, False otherwise
        """
        if self._setup_thread is not None:
            return False
        elif self._canvas is None:
            return True
        elif self._canvas.is_closeable():
            return self._check_close_world()
        else:
            log.info(
                f"The canvas in edit for world {self._world.level_wrapper.level_name} was not closeable for some reason."
            )
            return False

    def _check_close_world(self) -> bool:
        """
        Check if it is safe to close the world and prompt the user if it is not.
        :return: True if the world can be closed, False otherwise
        """
        unsaved_changes = self._world.history_manager.unsaved_changes
        if unsaved_changes:
            msg = wx.MessageDialog(
                self,
                f"""There {
                'is' if unsaved_changes == 1 else 'are'
                } {unsaved_changes} unsaved change{
                's' if unsaved_changes >= 2 else ''
                } in {
                self._world.level_wrapper.level_name
                }. Would you like to save?""",
                style=wx.YES_NO | wx.CANCEL | wx.CANCEL_DEFAULT,
            )
            response = msg.ShowModal()
            if response == wx.ID_YES:
                self._canvas.save()
                return True
            elif response == wx.ID_NO:
                return True
            elif response == wx.ID_CANCEL:
                log.info(f"""Aborting closing world {
                    self._world.level_wrapper.level_name
                    } because the user pressed cancel.""")
                return False
        return True

    def menu(self, menu: MenuData) -> MenuData:
        menu.setdefault(lang.get("menu_bar.file.menu_name"), {}).setdefault(
            "system", {}
        ).setdefault(
            self._menu_label(
                lang.get('program_3d_edit.menu_bar.file.save'),
                None,
                "Ctrl+S",
                "s",
            ),
            lambda evt: self._canvas.save(),
        )
        menu.setdefault(lang.get("menu_bar.file.menu_name"), {}).setdefault(
            "system", {}
        ).setdefault(
            self._menu_label(
                lang.get('action.act_save_as'),
                ACT_SAVE_AS,
                "Ctrl+Shift+S",
                "a",
            ),
            lambda evt: self._save_as(),
        )
        menu.setdefault(lang.get("menu_bar.file.menu_name"), {}).setdefault(
            "system", {}
        ).setdefault(
            self._menu_label(
                "Save All",
                ACT_SAVE_ALL,
                "Ctrl+Shift+A",
                "l",
            ),
            lambda evt: self._save_all(),
        )
        menu.setdefault(lang.get("menu_bar.file.menu_name"), {}).setdefault(
            "system", {}
        ).setdefault(
            self._menu_label(
                lang.get('action.act_save_all_close'),
                ACT_SAVE_ALL_CLOSE,
                "Ctrl+Shift+Q",
                "q",
            ),
            lambda evt: self._save_all_and_close(),
        )
        menu.setdefault(lang.get("menu_bar.file.menu_name"), {}).setdefault(
            "exit", {}
        ).setdefault(
            self._menu_label(
                lang.get('action.act_quit_without_save'),
                ACT_QUIT_WITHOUT_SAVE,
                "Ctrl+Alt+Shift+Q",
                "w",
            ),
            lambda evt: self._quit_without_save(),
        )
        # menu.setdefault(lang.get('menu_bar.file.menu_name'), {}).setdefault('system', {}).setdefault('Save As', lambda evt: self.GetGrandParent().close_world(self.world.world_path))

        menu.setdefault(
            lang.get("program_3d_edit.menu_bar.edit.menu_name"), {}
        ).setdefault("history", {}).update(
            {
                self._menu_label(lang.get('program_3d_edit.menu_bar.edit.undo'), None, "Ctrl+Z", "u"): lambda evt: self._canvas.undo(),
                self._menu_label(lang.get('program_3d_edit.menu_bar.edit.redo'), None, "Ctrl+Y", "r"): lambda evt: self._canvas.redo(),
            }
        )

        menu.setdefault(
            lang.get("program_3d_edit.menu_bar.edit.menu_name"), {}
        ).setdefault("operation", {}).update(
            {
                self._menu_label(lang.get('program_3d_edit.menu_bar.edit.cut'), None, "Ctrl+X", "t"): lambda evt: self._canvas.cut(),
                self._menu_label(lang.get('program_3d_edit.menu_bar.edit.copy'), None, "Ctrl+C", "c"): lambda evt: self._canvas.copy(),
                self._menu_label(
                    lang.get('program_3d_edit.menu_bar.edit.paste'),
                    ACT_PASTE,
                    "Ctrl+V",
                    "p",
                ): lambda evt: self._canvas.paste_from_cache(),
                self._menu_label(lang.get('program_3d_edit.menu_bar.edit.delete'), None, "Delete", "d"): lambda evt: self._canvas.delete(),
            }
        )

        menu.setdefault(
            lang.get("program_3d_edit.menu_bar.edit.menu_name"), {}
        ).setdefault("shortcut", {}).update(
            {
                self._menu_label(
                    lang.get('program_3d_edit.menu_bar.edit.deselect'),
                    ACT_DESELECT_BOX,
                    "Ctrl+D",
                    "e",
                ): lambda evt: self._canvas._deselect(),
                self._menu_label(
                    lang.get('program_3d_edit.menu_bar.edit.deselect_all'),
                    ACT_DESELECT_ALL_BOXES,
                    "Ctrl+Shift+A",
                    "l",
                ): lambda evt: self._canvas.deselect_all(),
                self._menu_label(lang.get('program_3d_edit.menu_bar.edit.select_all'), None, "Ctrl+A", "a"): lambda evt: self._canvas.select_all(),
            }
        )

        menu.setdefault(
            lang.get("program_3d_edit.menu_bar.navigation.menu_name"), {}
        ).setdefault("navigation", {}).update(
            {
                self._menu_label(
                    lang.get('program_3d_edit.menu_bar.navigation.toggle_projection'),
                    ACT_CHANGE_PROJECTION,
                    "`",
                    "p",
                ): lambda evt: self._toggle_projection(),
                self._menu_label(
                    lang.get('program_3d_edit.menu_bar.navigation.toggle_camera_cursor'),
                    ACT_TOGGLE_WASD_MODE,
                    "T",
                    "t",
                ): lambda evt: self._toggle_wasd_mode(),
                    self._menu_label(lang.get('program_3d_edit.menu_bar.navigation.goto'), None, "Ctrl+G", "c"): lambda evt: self._canvas.goto(),
                self._menu_label(
                    lang.get('action.act_move_camera_to_cursor'),
                    ACT_MOVE_CAMERA_TO_CURSOR,
                    "Ctrl+F",
                    "m",
                ): lambda evt: self._canvas._move_camera_to_selection_cursor(),
                self._menu_label(
                    lang.get('action.act_teleport_cursor_to_camera'),
                    ACT_TELEPORT_CURSOR_TO_CAMERA,
                    "Ctrl+Shift+F",
                    "h",
                ): lambda evt: self._canvas._teleport_selection_cursor_to_camera(),
            }
        )

        menu.setdefault(lang.get("menu_bar.file.menu_name"), {}).setdefault(
            "system", {}
        ).setdefault(
            self._menu_label(lang.get('program_3d_edit.menu_bar.file.preferences'), None, "Ctrl+P", "p"),
            lambda evt: self._edit_preferences(),
        )
        menu.setdefault(lang.get("menu_bar.options.menu_name"), {}).setdefault(
            "options", {}
        ).setdefault(
            self._menu_label(lang.get('program_3d_edit.menu_bar.options.keyboard_controls'), None, "Ctrl+K", "k"),
            lambda evt: self._edit_controls(),
        )
        menu.setdefault(lang.get("menu_bar.options.menu_name"), {}).setdefault(
            "options", {}
        ).setdefault(
            self._menu_label(lang.get('program_3d_edit.menu_bar.options.mouse_control'), None, "Ctrl+M", "m"),
            lambda evt: self._edit_mouse_control(),
        )
        menu.setdefault(lang.get("menu_bar.options.menu_name"), {}).setdefault(
            "options", {}
        ).setdefault(
            self._menu_label(lang.get('program_3d_edit.menu_bar.options.camera'), None, "Ctrl+I", "c"),
            lambda evt: self._edit_camera_controls(),
        )
        menu.setdefault(lang.get("menu_bar.help.menu_name"), {}).setdefault(
            "help", {}
        ).setdefault(
            self._menu_label(
                lang.get('program_3d_edit.menu_bar.help.user_guide'),
                ACT_HELP,
                "F1",
                "u",
            ),
            lambda evt: self._help_controls(),
        )
        return menu

    def _menu_label(
        self,
        text: str,
        action_id: Optional[str],
        fallback_hotkey: str,
        mnemonic: Optional[str] = None,
    ) -> str:
        # Normalize any pre-existing marker from translations and apply
        # the preferred mnemonic so entries are consistent in this menu.
        text = ensure_mnemonic(text.replace("&", ""), mnemonic)
        hotkey = self._action_hotkey(action_id, fallback_hotkey)
        return f"{text}\t{hotkey}" if hotkey else text

    def _action_hotkey(self, action_id: Optional[str], fallback_hotkey: str) -> str:
        if action_id and self._canvas is not None:
            keybind = self._canvas.key_binds.get(action_id)
            if keybind is not None:
                return self._format_hotkey(keybind)
        return fallback_hotkey

    @staticmethod
    def _format_hotkey(keybind) -> str:
        modifiers, trigger = keybind
        parts = [EditExtension._format_hotkey_part(modifier) for modifier in modifiers]
        parts.append(EditExtension._format_hotkey_part(trigger))
        return "+".join(parts)

    @staticmethod
    def _format_hotkey_part(part) -> str:
        text = str(part)
        replacements = {
            "CTRL": "Ctrl",
            "SHIFT": "Shift",
            "ALT": "Alt",
            "PAGE_UP": "PageUp",
            "PAGE_DOWN": "PageDown",
            "RETURN": "Enter",
            "BACK": "Backspace",
            "ESCAPE": "Esc",
            "DELETE": "Delete",
            "SPACE": "Space",
            "TAB": "Tab",
            "LEFT": "Left",
            "RIGHT": "Right",
            "UP": "Up",
            "DOWN": "Down",
        }
        if text in replacements:
            return replacements[text]
        if len(text) == 1:
            return text.upper()
        if text.startswith("F") and text[1:].isdigit():
            return text.upper()
        if "_" in text:
            return "".join(word.capitalize() for word in text.split("_"))
        return text

    def _on_char_hook(self, evt: wx.KeyEvent):
        """Handle key events before children to support global hotkeys."""
        if evt.ControlDown() and evt.ShiftDown() and evt.GetKeyCode() == ord('S'):
            self._save_as()
            return
        evt.Skip()

    def _save_as(self):
        parent = self.GetParent()
        if hasattr(parent, "_save_as"):
            parent._save_as()

    def _save_all(self):
        """Save all open worlds without closing."""
        if self._canvas is not None:
            self._canvas._save_all_worlds()

    def _save_all_and_close(self):
        if self._canvas is not None:
            self._canvas._save_all_worlds()
        close_level(self._world.level_path)

    def _quit_without_save(self):
        top_level_parent = self.GetTopLevelParent()
        if top_level_parent is not None:
            top_level_parent.Destroy()

    def _toggle_projection(self):
        """Toggle between perspective and top-down projection."""
        from amulet_map_editor.api.opengl.camera import Projection
        if self._canvas.camera.projection_mode == Projection.PERSPECTIVE:
            self._canvas.camera.rotation = 180, 90
            self._canvas.camera.projection_mode = Projection.TOP_DOWN
        elif self._canvas.camera.projection_mode == Projection.TOP_DOWN:
            self._canvas.camera.projection_mode = Projection.PERSPECTIVE

    def _toggle_wasd_mode(self):
        """Toggle between camera move and cursor move modes."""
        self._canvas.wasd_moves_cursor = not self._canvas.wasd_moves_cursor

    def _edit_controls(self):
        edit_config = config.get(EDIT_CONFIG_ID, {})
        keybind_id = edit_config.get(
            "keyboard_keybind_group",
            edit_config.get("keybind_group", DefaultKeybindGroupId),
        )
        user_keybinds = edit_config.get(
            "user_keyboard_keybinds",
            {
                group_id: {
                    action: key
                    for action, key in group.items()
                    if action in KeyboardKeys
                }
                for group_id, group in edit_config.get("user_keybinds", {}).items()
            },
        )
        fixed_keybinds = KeyboardPresets
        key_config = KeyConfigDialog(
            self,
            keybind_id,
            KeyboardKeys,
            fixed_keybinds,
            user_keybinds,
            KeyboardActionGroups,
            require_mouse_action=False,
        )
        key_config.SetTitle(lang.get("program_3d_edit.dialog.keyboard_mappings_title"))
        if key_config.ShowModal() == wx.ID_OK:
            user_keybinds, keybind_id, keybinds = key_config.options
            edit_config["user_keyboard_keybinds"] = user_keybinds
            edit_config["keyboard_keybind_group"] = keybind_id
            config.put(EDIT_CONFIG_ID, edit_config)
            # Register both keyboard and mouse bindings
            self._canvas.buttons.clear_registered_actions()
            mouse_keybind_id = edit_config.get(
                "mouse_keybind_group",
                edit_config.get("keybind_group", DefaultKeybindGroupId),
            )
            user_mouse_keybinds = edit_config.get(
                "user_mouse_keybinds",
                {
                    group_id: {
                        action: key
                        for action, key in group.items()
                        if action in MouseKeys
                    }
                    for group_id, group in edit_config.get("user_keybinds", {}).items()
                },
            )
            if mouse_keybind_id in user_mouse_keybinds:
                mouse_keybinds = user_mouse_keybinds[mouse_keybind_id]
            else:
                mouse_keybinds = MousePresets.get(mouse_keybind_id, {})
            # Combine keyboard and mouse bindings
            combined_keybinds = {**keybinds, **mouse_keybinds}
            self._canvas.buttons.register_actions(combined_keybinds)
            self._canvas.buttons.register_action(ACT_INCR_SPEED, tuple(), DOT)
            self._canvas.buttons.register_action(ACT_DECR_SPEED, tuple(), COMMA)
            self._canvas.buttons.register_action(ACT_ZOOM_IN, tuple(), DOT)
            self._canvas.buttons.register_action(ACT_ZOOM_OUT, tuple(), COMMA)

    def _edit_mouse_control(self):
        if self._canvas is not None:
            edit_config = config.get(EDIT_CONFIG_ID, {})
            keybind_id = edit_config.get(
                "mouse_keybind_group",
                edit_config.get("keybind_group", DefaultKeybindGroupId),
            )
            user_keybinds = edit_config.get(
                "user_mouse_keybinds",
                {
                    group_id: {
                        action: key
                        for action, key in group.items()
                        if action in MouseKeys
                    }
                    for group_id, group in edit_config.get("user_keybinds", {}).items()
                },
            )
            fixed_keybinds = MousePresets

            # Show mouse keybind configuration
            dialog = wx.Dialog(
                self,
                title=lang.get("program_3d_edit.dialog.mouse_mappings_title"),
                style=wx.CAPTION
                | wx.CLOSE_BOX
                | wx.MAXIMIZE_BOX
                | wx.MINIMIZE_BOX
                | wx.SYSTEM_MENU
                | wx.RESIZE_BORDER,
            )
            sizer = wx.BoxSizer(wx.VERTICAL)
            dialog.SetSizer(sizer)
            dialog_sizer = wx.BoxSizer(wx.VERTICAL)
            sizer.Add(dialog_sizer, 1, wx.EXPAND)

            key_config = KeyConfig(
                dialog,
                keybind_id,
                MouseKeys,
                fixed_keybinds,
                user_keybinds,
                MouseActionGroups,
                show_misc=False,
                show_descriptions=False,
                require_mouse_action=True,
            )
            dialog_sizer.Add(key_config, 1, wx.EXPAND)

            # Add bottom button sizer
            bottom_sizer = wx.BoxSizer(wx.HORIZONTAL)
            sizer.Add(bottom_sizer, 0, wx.EXPAND)
            bottom_sizer.AddStretchSpacer()
            button_sizer = dialog.CreateButtonSizer(wx.OK | wx.CANCEL)
            bottom_sizer.Add(button_sizer, flag=wx.ALL, border=5)

            dialog.Fit()

            if dialog.ShowModal() == wx.ID_OK:
                user_keybinds, keybind_id, mouse_keybinds = key_config.options
                edit_config["user_mouse_keybinds"] = user_keybinds
                edit_config["mouse_keybind_group"] = keybind_id
                config.put(EDIT_CONFIG_ID, edit_config)

                # Register both keyboard and mouse bindings
                self._canvas.buttons.clear_registered_actions()
                keyboard_keybind_id = edit_config.get(
                    "keyboard_keybind_group",
                    edit_config.get("keybind_group", DefaultKeybindGroupId),
                )
                user_keyboard_keybinds = edit_config.get(
                    "user_keyboard_keybinds",
                    {
                        group_id: {
                            action: key
                            for action, key in group.items()
                            if action in KeyboardKeys
                        }
                        for group_id, group in edit_config.get("user_keybinds", {}).items()
                    },
                )
                if keyboard_keybind_id in user_keyboard_keybinds:
                    keyboard_keybinds = user_keyboard_keybinds[keyboard_keybind_id]
                else:
                    keyboard_keybinds = KeyboardPresets.get(keyboard_keybind_id, {})
                combined_keybinds = {**keyboard_keybinds, **mouse_keybinds}
                self._canvas.buttons.register_actions(combined_keybinds)
                self._canvas.buttons.register_action(ACT_INCR_SPEED, tuple(), DOT)
                self._canvas.buttons.register_action(ACT_DECR_SPEED, tuple(), COMMA)

    def _edit_camera_controls(self):
        if self._canvas is not None:
            fov = self._canvas.camera.perspective_fov
            render_distance = self._canvas.renderer.render_distance
            dialog = SimpleDialog(self, "Camera Controls")

            sizer = wx.FlexGridSizer(2, 2, 0, 0)
            dialog.sizer.Add(sizer, flag=wx.ALL, border=5)
            fov_ui = wx.SpinCtrlDouble(dialog, min=0, max=180, initial=fov)

            def set_fov(evt):
                self._canvas.camera.perspective_fov = fov_ui.GetValue()

            fov_ui.Bind(wx.EVT_SPINCTRLDOUBLE, set_fov)
            sizer.Add(
                wx.StaticText(dialog, label="Field of View"),
                flag=wx.LEFT | wx.TOP | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND,
                border=5,
            )
            sizer.Add(
                fov_ui,
                flag=wx.LEFT | wx.TOP | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND,
                border=5,
            )

            render_distance_ui = wx.SpinCtrl(
                dialog, min=0, max=500, initial=render_distance
            )

            def set_render_distance(evt):
                self._canvas.renderer.render_distance = render_distance_ui.GetValue()

            render_distance_ui.Bind(wx.EVT_SPINCTRL, set_render_distance)
            sizer.Add(
                wx.StaticText(dialog, label="Render Distance"),
                flag=wx.LEFT | wx.TOP | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND,
                border=5,
            )
            sizer.Add(
                render_distance_ui,
                flag=wx.LEFT | wx.TOP | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND,
                border=5,
            )

            dialog.Fit()

            response = dialog.ShowModal()
            if response == wx.ID_OK:
                edit_config.setdefault("options", {})
                edit_config["options"]["fov"] = fov_ui.GetValue()
                edit_config["options"][
                    "render_distance"
                ] = render_distance_ui.GetValue()
                config.put(EDIT_CONFIG_ID, edit_config)
            elif response == wx.ID_CANCEL:
                self._canvas.camera.perspective_fov = fov
                self._canvas.renderer.render_distance = render_distance

    def _edit_preferences(self):
        edit_config: dict = config.get(EDIT_CONFIG_ID, {})
        options = edit_config.get("options", {})
        recent_worlds_limit = (
            options.get(
                "recent_worlds_limit", DEFAULT_RECENT_WORLDS_LIMIT
            )
        )
        if not isinstance(recent_worlds_limit, int) or recent_worlds_limit < 1:
            recent_worlds_limit = DEFAULT_RECENT_WORLDS_LIMIT

        dialog = SimpleDialog(self, "Preferences")
        sizer = wx.FlexGridSizer(0, 2, 0, 0)
        sizer.AddGrowableCol(1, 1)
        dialog.sizer.Add(sizer, flag=wx.ALL, border=5)

        recent_worlds_limit_ui = wx.SpinCtrl(
            dialog, min=1, max=100, initial=recent_worlds_limit
        )
        sizer.Add(
            wx.StaticText(dialog, label="Recent Worlds Limit"),
            flag=wx.LEFT | wx.TOP | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND,
            border=5,
        )
        sizer.Add(
            recent_worlds_limit_ui,
            flag=wx.LEFT | wx.TOP | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND,
            border=5,
        )

        box_colours = options.get("box_colours", {}) if isinstance(options, dict) else {}

        def add_colour_picker(label: str, pref_key: str, legacy_keys: tuple = ()): 
            default_colour = _BOX_COLOUR_DEFAULTS[pref_key]
            pref_value = box_colours.get(pref_key)
            if pref_value is None:
                for legacy_key in legacy_keys:
                    pref_value = box_colours.get(legacy_key)
                    if pref_value is not None:
                        break
            current_colour = self._colour_pref_to_float(
                pref_value, default_colour
            )
            picker = wx.ColourPickerCtrl(
                dialog,
                colour=wx.Colour(
                    int(current_colour[0] * 255),
                    int(current_colour[1] * 255),
                    int(current_colour[2] * 255),
                ),
            )
            sizer.Add(
                wx.StaticText(dialog, label=label),
                flag=wx.LEFT | wx.TOP | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND,
                border=5,
            )
            sizer.Add(
                picker,
                flag=wx.LEFT | wx.TOP | wx.ALIGN_CENTER_VERTICAL | wx.EXPAND,
                border=5,
            )
            return picker

        mouse_cursor_picker = add_colour_picker("Mouse Cursor Color", "mouse_cursor")
        clipboard_static_picker = add_colour_picker("Clipboard Color", "clipboard_static")
        moving_object_picker = add_colour_picker(
            "Moving Object", "moving_object", ("clipboard",)
        )
        point1_picker = add_colour_picker("Point 1 Color", "point1")
        point2_picker = add_colour_picker("Point 2 Color", "point2")
        edge_picker = add_colour_picker("Edge Color", "edge")
        corner_picker = add_colour_picker("Corner Color", "corner")

        dialog.Fit()

        if dialog.ShowModal() == wx.ID_OK:
            edit_config.setdefault("options", {})
            edit_config["options"]["recent_worlds_limit"] = (
                recent_worlds_limit_ui.GetValue()
            )
            edit_config["options"]["box_colours"] = {
                "mouse_cursor": [
                    mouse_cursor_picker.GetColour().Red(),
                    mouse_cursor_picker.GetColour().Green(),
                    mouse_cursor_picker.GetColour().Blue(),
                ],
                "clipboard_static": [
                    clipboard_static_picker.GetColour().Red(),
                    clipboard_static_picker.GetColour().Green(),
                    clipboard_static_picker.GetColour().Blue(),
                ],
                "point1": [
                    point1_picker.GetColour().Red(),
                    point1_picker.GetColour().Green(),
                    point1_picker.GetColour().Blue(),
                ],
                "point2": [
                    point2_picker.GetColour().Red(),
                    point2_picker.GetColour().Green(),
                    point2_picker.GetColour().Blue(),
                ],
                "moving_object": [
                    moving_object_picker.GetColour().Red(),
                    moving_object_picker.GetColour().Green(),
                    moving_object_picker.GetColour().Blue(),
                ],
                "edge": [
                    edge_picker.GetColour().Red(),
                    edge_picker.GetColour().Green(),
                    edge_picker.GetColour().Blue(),
                ],
                "corner": [
                    corner_picker.GetColour().Red(),
                    corner_picker.GetColour().Green(),
                    corner_picker.GetColour().Blue(),
                ],
            }
            self._apply_box_colour_preferences(edit_config["options"])
            config.put(EDIT_CONFIG_ID, edit_config)

    @staticmethod
    def _help_controls():
        webbrowser.open(
            "https://github.com/Amulet-Team/Amulet-Map-Editor/blob/master/amulet_map_editor/programs/edit/readme.md"
        )
