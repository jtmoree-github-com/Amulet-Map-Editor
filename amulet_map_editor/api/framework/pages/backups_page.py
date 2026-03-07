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

        self._backup_folder = self._backup_config.get(
            BACKUP_DIR_KEY, os.path.expanduser("~")
        )
        self._worlds_folder = self._backup_config.get(
            WORLDS_DIR_KEY, _default_worlds_folder()
        )

        root = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(root)

        title = wx.StaticText(self, label="Backups")
        title_font = title.GetFont()
        title_font.SetPointSize(title_font.GetPointSize() + 4)
        title.SetFont(title_font)
        root.Add(title, 0, wx.ALL, 10)

        form = wx.FlexGridSizer(2, 3, 8, 8)
        form.AddGrowableCol(1, 1)
        root.Add(form, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        form.Add(
            wx.StaticText(self, label="Backup folder:"),
            0,
            wx.ALIGN_CENTER_VERTICAL,
        )
        self._backup_folder_text = wx.TextCtrl(self, value=self._backup_folder)
        form.Add(self._backup_folder_text, 1, wx.EXPAND)
        backup_browse = wx.Button(self, label="Browse...")
        backup_browse.Bind(wx.EVT_BUTTON, self._browse_backup_folder)
        form.Add(backup_browse, 0)

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

        root.AddStretchSpacer(1)

        self._save_button = wx.Button(self, label="Save")
        self._save_button.Bind(wx.EVT_BUTTON, lambda evt: self._save_settings())
        root.Add(self._save_button, 0, wx.ALL | wx.ALIGN_RIGHT, 10)

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

    def _save_settings(self) -> None:
        self._backup_config[BACKUP_DIR_KEY] = self._backup_folder_text.GetValue().strip()
        self._backup_config[WORLDS_DIR_KEY] = self._worlds_folder_text.GetValue().strip()
        self._meta[BACKUP_CONFIG_GROUP] = self._backup_config
        config.put("amulet_meta", self._meta)

    def _browse_backup_folder(self, _evt):
        default_path = self._backup_folder_text.GetValue().strip() or os.path.expanduser("~")
        with wx.DirDialog(
            self,
            "Choose backup folder",
            defaultPath=default_path,
            style=wx.DD_DEFAULT_STYLE,
        ) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return
            self._backup_folder_text.SetValue(dlg.GetPath())
            self._save_settings()

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
