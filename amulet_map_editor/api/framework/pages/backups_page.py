import os
import zipfile
from datetime import datetime

import wx

from amulet_map_editor.api import config
from amulet_map_editor.api.framework.pages.base_page import BasePageUI
from amulet_map_editor.api.wx.ui.selectable_message_dialog import SelectableMessageBox


BACKUP_CONFIG_GROUP = "backup"
BACKUP_DIR_KEY = "backup_folder"
WORLDS_DIR_KEY = "worlds_folder"


def _default_worlds_folder() -> str:
    from amulet_map_editor.api.wx.ui.select_world import minecraft_world_paths

    for _, path in minecraft_world_paths:
        if os.path.isdir(path):
            return path
    return os.path.expanduser("~")


def perform_backup(parent: wx.Window = None) -> None:
    """
    Perform a backup using the saved configuration.
    If configuration is missing or invalid, show an error.
    
    :param parent: Parent window for dialogs (optional)
    """
    meta = config.get("amulet_meta", {})
    backup_config = meta.get(BACKUP_CONFIG_GROUP, {})
    
    backup_folder = backup_config.get(BACKUP_DIR_KEY, "").strip()
    worlds_folder = backup_config.get(WORLDS_DIR_KEY, "").strip()
    
    # Validate settings
    if not backup_folder:
        SelectableMessageBox(
            "Backup folder not configured.\n\nPlease open Backup Settings and configure the folders.",
            "Backup Error",
            wx.OK | wx.ICON_ERROR,
            parent=parent
        )
        return
    
    if not worlds_folder:
        SelectableMessageBox(
            "Minecraft worlds folder not configured.\n\nPlease open Backup Settings and configure the folders.",
            "Backup Error",
            wx.OK | wx.ICON_ERROR,
            parent=parent
        )
        return
    
    if not os.path.isdir(worlds_folder):
        SelectableMessageBox(
            f"Minecraft worlds folder does not exist:\n{worlds_folder}\n\nPlease open Backup Settings and verify the folders.",
            "Backup Error",
            wx.OK | wx.ICON_ERROR,
            parent=parent
        )
        return
    
    # Create backup folder if it doesn't exist
    os.makedirs(backup_folder, exist_ok=True)
    
    # Create timestamped backup filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    zip_path = os.path.join(backup_folder, f"{timestamp}.zip")
    
    # Show progress dialog
    progress = wx.ProgressDialog(
        "Backups",
        "Creating backup archive...",
        maximum=100,
        parent=parent,
        style=wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME | wx.PD_AUTO_HIDE,
    )
    
    try:
        # Collect all files to backup
        file_paths = []
        for root, _dirs, files in os.walk(worlds_folder):
            for file_name in files:
                file_paths.append(os.path.join(root, file_name))
        
        # Create zip archive
        total = max(len(file_paths), 1)
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for index, abs_path in enumerate(file_paths, start=1):
                rel_path = os.path.relpath(abs_path, worlds_folder)
                zf.write(abs_path, rel_path)
                percent = int(index * 100 / total)
                progress.Update(percent, f"Backing up {index}/{total} files...")
    
    except Exception as e:
        # Clean up partial backup on error
        if os.path.exists(zip_path):
            try:
                os.remove(zip_path)
            except Exception:
                pass
        SelectableMessageBox(
            f"Backup failed:\n{e}",
            "Backup Error",
            wx.OK | wx.ICON_ERROR,
            parent=parent
        )
    else:
        # Success!
        SelectableMessageBox(
            f"Backup created:\n{zip_path}",
            "Backups",
            wx.OK | wx.ICON_INFORMATION,
            parent=parent
        )
    finally:
        progress.Destroy()


class BackupsPageUI(wx.Panel, BasePageUI):
    """UI page for creating zip backups of an entire worlds directory."""

    def __init__(self, parent: wx.Window):
        super().__init__(parent)
        self._parent_notebook = parent
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

        self._meta = config.get("amulet_meta", {})
        self._backup_config = self._meta.setdefault(BACKUP_CONFIG_GROUP, {})

        # Get the backup folder from preferences
        self._backup_folder = self._backup_config.get(
            BACKUP_DIR_KEY, os.path.expanduser("~")
        )

        root = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(root)

        title = wx.StaticText(self, label="Backups")
        title_font = title.GetFont()
        title_font.SetPointSize(title_font.GetPointSize() + 4)
        title.SetFont(title_font)
        root.Add(title, 0, wx.ALL, 10)

        # Display backup folder (read-only)
        info_sizer = wx.BoxSizer(wx.VERTICAL)
        root.Add(info_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        info_sizer.Add(
            wx.StaticText(self, label="Backup folder:"),
            0,
            wx.BOTTOM,
            5,
        )
        
        backup_folder_text = wx.TextCtrl(
            self, value=self._backup_folder, style=wx.TE_READONLY
        )
        info_sizer.Add(backup_folder_text, 0, wx.EXPAND | wx.BOTTOM, 10)

        info_sizer.Add(
            wx.StaticText(
                self,
                label="To change the backup folder, use Preferences (Ctrl+P).",
            ),
            0,
            wx.BOTTOM,
            10,
        )

        root.AddStretchSpacer(1)

        self._backup_button = wx.Button(self, label="Create Backup")
        self._backup_button.Bind(wx.EVT_BUTTON, lambda evt: self._do_backup())
        root.Add(self._backup_button, 0, wx.ALL | wx.ALIGN_RIGHT, 10)

    def _close_backups_tab(self):
        if hasattr(self._parent_notebook, "close_backups_tab"):
            self._parent_notebook.close_backups_tab()

    def _on_char_hook(self, evt: wx.KeyEvent):
        key_code = evt.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
            self._close_backups_tab()
            return

        if (
            key_code in (ord("Q"), ord("q"))
            and evt.ControlDown()
            and not evt.ShiftDown()
            and not evt.AltDown()
        ):
            self._close_backups_tab()
            return

        evt.Skip()

    def enable(self):
        """Run when the tab is shown/enabled. Refresh menu to remove Edit/Camera menus."""
        self.GetTopLevelParent().create_menu()

    def _do_backup(self) -> None:
        """Perform a backup operation."""
        perform_backup(parent=self)
