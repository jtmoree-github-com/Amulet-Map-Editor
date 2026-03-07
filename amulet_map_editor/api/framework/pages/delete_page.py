import os
import glob
import shutil

import wx

from amulet import load_format
from amulet.api.errors import FormatError

from amulet_map_editor.api import config
from amulet_map_editor.api.framework.pages.base_page import BasePageUI


DELETE_CONFIG_GROUP = "delete"
WORLDS_DIR_KEY = "worlds_folder"


def _default_worlds_folder() -> str:
    from amulet_map_editor.api.wx.ui.select_world import minecraft_world_paths

    for _, path in minecraft_world_paths:
        if os.path.isdir(path):
            return path
    return os.path.expanduser("~")


class DeletePageUI(wx.Panel, BasePageUI):
    """UI page for deleting Minecraft worlds."""

    def __init__(self, parent: wx.Window):
        super().__init__(parent)
        self._parent_notebook = parent
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

        self._meta = config.get("amulet_meta", {})
        self._delete_config = self._meta.setdefault(DELETE_CONFIG_GROUP, {})

        self._worlds_folder = self._delete_config.get(
            WORLDS_DIR_KEY, _default_worlds_folder()
        )

        root = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(root)

        title = wx.StaticText(self, label="Delete Worlds")
        title_font = title.GetFont()
        title_font.SetPointSize(title_font.GetPointSize() + 4)
        title.SetFont(title_font)
        root.Add(title, 0, wx.ALL, 10)

        form = wx.FlexGridSizer(1, 3, 8, 8)
        form.AddGrowableCol(1, 1)
        root.Add(form, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        form.Add(
            wx.StaticText(self, label="Minecraft worlds folder:"),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )
        self._worlds_folder_text = wx.TextCtrl(self, value=self._worlds_folder)
        form.Add(self._worlds_folder_text, 1, wx.EXPAND)
        worlds_browse = wx.Button(self, label="Browse...")
        worlds_browse.Bind(wx.EVT_BUTTON, self._browse_worlds_folder)
        form.Add(worlds_browse, 0)

        refresh_button = wx.Button(self, label="Refresh World List")
        refresh_button.Bind(wx.EVT_BUTTON, self._refresh_worlds)
        root.Add(refresh_button, 0, wx.ALL | wx.ALIGN_RIGHT, 10)

        # Scrollable panel for world list
        self._scroll_panel = wx.ScrolledWindow(self, style=wx.VSCROLL)
        self._scroll_panel.SetScrollRate(0, 20)
        root.Add(self._scroll_panel, 1, wx.EXPAND | wx.ALL, 10)

        self._worlds_sizer = wx.BoxSizer(wx.VERTICAL)
        self._scroll_panel.SetSizer(self._worlds_sizer)

        self._refresh_worlds(None)

    def _close_delete_tab(self):
        if hasattr(self._parent_notebook, "close_delete_tab"):
            self._parent_notebook.close_delete_tab()

    def _on_char_hook(self, evt: wx.KeyEvent):
        key_code = evt.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
            self._close_delete_tab()
            return

        if (
            key_code in (ord("Q"), ord("q"))
            and evt.ControlDown()
            and not evt.ShiftDown()
            and not evt.AltDown()
        ):
            self._close_delete_tab()
            return

        evt.Skip()

    def _save_settings(self) -> None:
        self._delete_config[WORLDS_DIR_KEY] = self._worlds_folder_text.GetValue().strip()
        self._meta[DELETE_CONFIG_GROUP] = self._delete_config
        config.put("amulet_meta", self._meta)

    def _browse_worlds_folder(self, _evt):
        default_path = self._worlds_folder_text.GetValue().strip() or _default_worlds_folder()
        with wx.DirDialog(
            self,
            "Choose Minecraft worlds folder",
            defaultPath=default_path,
            style=wx.DD_DEFAULT_STYLE,
        ) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return
            self._worlds_folder_text.SetValue(dlg.GetPath())
            self._save_settings()
            self._refresh_worlds(None)

    def _refresh_worlds(self, _evt):
        # Clear existing world entries
        self._worlds_sizer.Clear(True)

        worlds_folder = self._worlds_folder_text.GetValue().strip()

        if not worlds_folder:
            self._worlds_sizer.Add(
                wx.StaticText(self._scroll_panel, label="No worlds folder specified."),
                0,
                wx.ALL,
                5,
            )
            self._scroll_panel.Layout()
            self._scroll_panel.FitInside()
            return

        if not os.path.isdir(worlds_folder):
            self._worlds_sizer.Add(
                wx.StaticText(
                    self._scroll_panel,
                    label=f"Worlds folder does not exist:\n{worlds_folder}",
                ),
                0,
                wx.ALL,
                5,
            )
            self._scroll_panel.Layout()
            self._scroll_panel.FitInside()
            return

        # Find all worlds in the folder
        world_paths = []
        for world_path in glob.glob(os.path.join(glob.escape(worlds_folder), "*")):
            if os.path.isdir(world_path):
                try:
                    world_format = load_format(world_path)
                    world_paths.append((world_format.level_name, world_format.game_version_string, world_path))
                except (FormatError, Exception):
                    # Not a valid world or error reading it
                    pass

        if not world_paths:
            self._worlds_sizer.Add(
                wx.StaticText(self._scroll_panel, label="No worlds found in this folder."),
                0,
                wx.ALL,
                5,
            )
            self._scroll_panel.Layout()
            self._scroll_panel.FitInside()
            return

        # Sort alphabetically by world name
        world_paths.sort(key=lambda x: x[0].lower())

        # Add each world with a delete button
        for world_name, game_version, world_path in world_paths:
            world_panel = wx.Panel(self._scroll_panel)
            world_sizer = wx.BoxSizer(wx.HORIZONTAL)
            world_panel.SetSizer(world_sizer)

            world_label = wx.StaticText(
                world_panel,
                label=f"{world_name} ({game_version})"
            )
            world_label.SetMinSize((400, -1))
            world_sizer.Add(world_label, 1, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

            delete_button = wx.Button(world_panel, label="Delete")
            delete_button.Bind(wx.EVT_BUTTON, lambda evt, path=world_path, name=world_name: self._delete_world(path, name))
            world_sizer.Add(delete_button, 0, wx.ALL, 5)

            self._worlds_sizer.Add(world_panel, 0, wx.EXPAND | wx.ALL, 2)

        self._scroll_panel.Layout()
        self._scroll_panel.FitInside()

    def _delete_world(self, world_path: str, world_name: str):
        # Show confirmation dialog
        dlg = wx.MessageDialog(
            self,
            f"Are you sure you want to delete:\n\n{world_name}\n\nPath: {world_path}\n\nThis action cannot be undone!",
            "Confirm World Deletion",
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING
        )
        
        # Change button labels
        dlg.SetYesNoLabels("YES DELETE THIS WORLD. I AM SURE", "Cancel")
        
        result = dlg.ShowModal()
        dlg.Destroy()

        if result != wx.ID_YES:
            return

        # Delete the world
        try:
            shutil.rmtree(world_path)
            wx.MessageBox(
                f"World deleted successfully:\n{world_name}",
                "Delete Complete",
                wx.OK | wx.ICON_INFORMATION
            )
            # Refresh the list
            self._refresh_worlds(None)
        except Exception as e:
            wx.MessageBox(
                f"Failed to delete world:\n{e}",
                "Delete Error",
                wx.OK | wx.ICON_ERROR
            )
