from __future__ import annotations
import wx
from wx.lib.agw import flatnotebook
from typing import Dict, Union
import traceback
import logging
import sys
import platform
import os

from amulet.api.errors import LoaderNoneMatched
from amulet_map_editor.api.wx.ui.select_world import open_level_from_dialog, WorldSelectPageUI
from amulet_map_editor.api.wx.ui.traceback_dialog import TracebackDialog
from amulet_map_editor import __version__, lang
from amulet_map_editor.api.framework.pages import WorldPageUI
from .pages import AmuletMainMenu, BackupsPageUI, DeletePageUI, BasePageUI

from amulet_map_editor.api import image
from amulet_map_editor.api import config
from amulet_map_editor.api.wx.ui.simple import SimpleDialog
from amulet_map_editor.api.wx.util.ui_preferences import preserve_ui_preferences

log = logging.getLogger(__name__)

NOTEBOOK_MENU_STYLE = (
    flatnotebook.FNB_NO_X_BUTTON
    | flatnotebook.FNB_HIDE_ON_SINGLE_TAB
    | flatnotebook.FNB_NAV_BUTTONS_WHEN_NEEDED
)
NOTEBOOK_STYLE = NOTEBOOK_MENU_STYLE | flatnotebook.FNB_X_ON_TAB

CLOSEABLE_PAGE_TYPE = Union[WorldPageUI]
EDIT_CONFIG_ID = "amulet_edit"
DEFAULT_RECENT_WORLDS_LIMIT = 5

wx.Image.SetDefaultLoadFlags(0)


@preserve_ui_preferences
class AmuletUI(wx.Frame):
    """This is the top level frame that Amulet exists within."""

    # The notebook to hold world pages
    _level_notebook: AmuletLevelNotebook

    def __init__(self, parent):
        title = f"Amulet {__version__}"
        if not getattr(sys, "frozen", False):
            title += " (source)"
        wx.Frame.__init__(
            self,
            parent,
            id=wx.ID_ANY,
            title=title,
            pos=wx.DefaultPosition,
            size=wx.Size(1000, 600),
            style=wx.CAPTION
            | wx.CLOSE_BOX
            | wx.MINIMIZE_BOX
            | wx.MAXIMIZE_BOX
            | wx.SYSTEM_MENU
            | wx.TAB_TRAVERSAL
            | wx.CLIP_CHILDREN
            | wx.RESIZE_BORDER,
        )
        self.SetMinSize((570, 620))
        icon = wx.Icon()
        icon.CopyFromBitmap(image.logo.amulet_logo.bitmap())
        self.SetIcon(icon)

        self._level_notebook = AmuletLevelNotebook(self, agwStyle=NOTEBOOK_MENU_STYLE)
        self._level_notebook.init()
        self.Layout()

        self.Bind(wx.EVT_CLOSE, self._level_notebook.on_app_close)
        
        # Set up accelerator table for global hotkeys
        self._setup_accelerators()

        # Register an OS-level hotkey for Ctrl+Alt+Shift+Q so it fires
        # even when a modal dialog is open.
        self._HOTKEY_FORCE_QUIT_ID = wx.NewIdRef()
        if platform.system() == "Windows":
            self.RegisterHotKey(
                self._HOTKEY_FORCE_QUIT_ID,
                wx.MOD_CONTROL | wx.MOD_ALT | wx.MOD_SHIFT,
                ord('Q'),
            )
            self.Bind(wx.EVT_HOTKEY, self._on_hotkey_force_quit, id=self._HOTKEY_FORCE_QUIT_ID)

    def open_level(self, path: str):
        """Open a level. You should use the method in the app."""
        self._level_notebook.open_level(path)

    def _setup_accelerators(self):
        """Setup global keyboard accelerators for tab navigation."""
        # Use fixed IDs for reliability
        ID_CTRL_PAGEDOWN = 10001
        ID_CTRL_PAGEUP = 10002
        ID_CTRL_SHIFT_PAGEDOWN = 10003
        ID_CTRL_SHIFT_PAGEUP = 10004
        ID_CTRL_Q = 10005
        ID_CTRL_ALT_SHIFT_Q = 10006
        
        acc_entries = [
            wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_PAGEDOWN, ID_CTRL_PAGEDOWN),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, wx.WXK_PAGEUP, ID_CTRL_PAGEUP),
            wx.AcceleratorEntry(wx.ACCEL_CTRL | wx.ACCEL_SHIFT, wx.WXK_PAGEDOWN, ID_CTRL_SHIFT_PAGEDOWN),
            wx.AcceleratorEntry(wx.ACCEL_CTRL | wx.ACCEL_SHIFT, wx.WXK_PAGEUP, ID_CTRL_SHIFT_PAGEUP),
            wx.AcceleratorEntry(wx.ACCEL_CTRL, ord('Q'), ID_CTRL_Q),
            wx.AcceleratorEntry(wx.ACCEL_CTRL | wx.ACCEL_ALT | wx.ACCEL_SHIFT, ord('Q'), ID_CTRL_ALT_SHIFT_Q),
        ]
        
        accel_table = wx.AcceleratorTable(acc_entries)
        self.SetAcceleratorTable(accel_table)
        
        # Bind the accelerator events
        self.Bind(wx.EVT_MENU, self._on_accel_ctrl_pagedown, id=ID_CTRL_PAGEDOWN)
        self.Bind(wx.EVT_MENU, self._on_accel_ctrl_pageup, id=ID_CTRL_PAGEUP)
        self.Bind(wx.EVT_MENU, self._on_accel_ctrl_shift_pagedown, id=ID_CTRL_SHIFT_PAGEDOWN)
        self.Bind(wx.EVT_MENU, self._on_accel_ctrl_shift_pageup, id=ID_CTRL_SHIFT_PAGEUP)
        self.Bind(wx.EVT_MENU, self._on_accel_ctrl_q, id=ID_CTRL_Q)
        self.Bind(wx.EVT_MENU, self._on_accel_ctrl_alt_shift_q, id=ID_CTRL_ALT_SHIFT_Q)
    
    def _on_accel_ctrl_pagedown(self, evt):
        """Handle Ctrl+PageDown - next world."""
        self._navigate_notebooks(1)
    
    def _on_accel_ctrl_pageup(self, evt):
        """Handle Ctrl+PageUp - previous world."""
        self._navigate_notebooks(-1)
    
    def _on_accel_ctrl_shift_pagedown(self, evt):
        """Handle Ctrl+Shift+PageDown - next tab in current world."""
        self._navigate_world_tabs(1)
    
    def _on_accel_ctrl_shift_pageup(self, evt):
        """Handle Ctrl+Shift+PageUp - previous tab in current world."""
        self._navigate_world_tabs(-1)
    
    def _navigate_world_tabs(self, direction):
        """Navigate tabs within the current world (1 for next, -1 for prev)."""
        current_page = self._level_notebook.GetSelection()
        if current_page == wx.NOT_FOUND:
            return
        
        current_tab = self._level_notebook.GetPage(current_page)
        
        # Check if current tab is a WorldPageUI
        if isinstance(current_tab, WorldPageUI):
            page_count = current_tab.GetPageCount()
            if page_count > 1:
                selection = current_tab.GetSelection()
                next_page = (selection + direction) % page_count
                current_tab.SetSelection(next_page)
    
    def _navigate_notebooks(self, direction):
        """Navigate between worlds and main menu (1 for next, -1 for prev)."""
        page_count = self._level_notebook.GetPageCount()
        if page_count > 1:
            selection = self._level_notebook.GetSelection()
            next_page = (selection + direction) % page_count
            self._level_notebook.SetSelection(next_page)
    
    def _on_accel_ctrl_q(self, evt):
        """Handle Ctrl+Q - close current world or quit if on main menu."""
        current_page = self._level_notebook.GetCurrentPage()
        if isinstance(current_page, WorldPageUI):
            self.close_level(current_page.path)
        elif current_page is self._level_notebook._world_selector:
            self._level_notebook.close_world_select_tab()
        elif current_page is self._level_notebook._backups_page:
            self._level_notebook.close_backups_tab()
        elif current_page is self._level_notebook._delete_page:
            self._level_notebook.close_delete_tab()
        elif current_page is self._level_notebook._main_menu:
            self.Close()

    def _on_accel_ctrl_alt_shift_q(self, evt):
        """Handle Ctrl+Alt+Shift+Q - force quit without saving or prompts."""
        self.force_quit_without_save()

    def _on_hotkey_force_quit(self, evt):
        """Handle OS-level hotkey for force quit (works over modal dialogs)."""
        self.force_quit_without_save()

    def force_quit_without_save(self):
        """Force close all dialogs and the main window without saving."""
        self._level_notebook._force_quit_without_save = True

        # Close all modal and modeless dialogs first so they don't block
        # the frame from closing.
        for win in wx.GetTopLevelWindows():
            if isinstance(win, wx.Dialog):
                try:
                    if win.IsModal():
                        win.EndModal(wx.ID_CANCEL)
                    else:
                        win.Close(force=True)
                except Exception:
                    pass

        self.Close(force=True)

    def open_world_select_tab(self):
        """Open the world selector as a tab. You should use the method in the app."""
        self._level_notebook.open_world_select_tab()

    def open_backups_tab(self):
        """Open the backups tab."""
        self._level_notebook.open_backups_tab()

    def open_delete_tab(self):
        """Open the delete worlds tab."""
        self._level_notebook.open_delete_tab()

    def close_world_select_tab(self):
        """Close the world selector tab if open."""
        self._level_notebook.close_world_select_tab()

    def close_backups_tab(self):
        """Close the backups tab if open."""
        self._level_notebook.close_backups_tab()

    def close_delete_tab(self):
        """Close the delete worlds tab if open."""
        self._level_notebook.close_delete_tab()

    def close_level(self, path: str):
        """Close a given level. You should use the method in the app."""
        self._level_notebook.close_level(path)

    @staticmethod
    def _mru_display_name(world_path: str) -> str:
        """Get a display name for MRU entries.

        Prefer Bedrock's levelname.txt when available, then fall back to
        folder/file name.
        """
        level_name_file = os.path.join(world_path, "levelname.txt")
        if os.path.isfile(level_name_file):
            try:
                with open(level_name_file, "r", encoding="utf-8") as f:
                    name = f.read().strip()
                if name:
                    return name
            except Exception:
                pass

        return os.path.basename(world_path.rstrip("\\/")) or world_path

    def create_menu(self):
        """
        Create the UI menu.

        Adds the top level menu items then extends it from the active page
        """
        menu_dict = {}
        menu_dict.setdefault(lang.get("menu_bar.file.menu_name"), {}).setdefault(
            "system", {}
        ).setdefault(
            f"&{lang.get('menu_bar.file.open_world')}\tCtrl+O",
            lambda evt: self.open_world_select_tab(),
        )

        # Only show Preferences on the main menu tab.
        if self._level_notebook.GetCurrentPage() is self._level_notebook._main_menu:
            menu_dict.setdefault(lang.get("menu_bar.file.menu_name"), {}).setdefault(
                "system", {}
            ).setdefault(
                "&Preferences\tCtrl+P",
                lambda evt: self._edit_preferences(),
            )

        # Add MRU worlds to the File menu.
        meta_config = config.get("amulet_meta", {})
        recent_worlds = meta_config.get("recent_worlds", [])
        if isinstance(recent_worlds, list):
            recent_menu = menu_dict.setdefault(
                lang.get("menu_bar.file.menu_name"), {}
            ).setdefault("recent", {})

            if recent_worlds:
                for index, world_path in enumerate(recent_worlds[:10], start=1):
                    if not isinstance(world_path, str):
                        continue
                    label_name = self._mru_display_name(world_path)
                    menu_label = f"&{index} {label_name}"
                    recent_menu.setdefault(
                        menu_label,
                        lambda evt, path=world_path: self.open_level(path),
                    )
            else:
                # Placeholder when there are no recent worlds yet.
                recent_menu.setdefault("(No recent worlds)", lambda evt: None)

        # menu_dict.setdefault(lang.get('menu_bar.file.menu_name'), {}).setdefault('system', {}).setdefault('Create World', lambda: self.world.save())
        menu_dict = self._level_notebook.extend_menu(menu_dict)
        menu_bar = wx.MenuBar()
        for menu_name, menu_data in menu_dict.items():
            menu = wx.Menu()
            separator = False
            for menu_section in menu_data.values():
                if separator:
                    menu.AppendSeparator()
                separator = True
                for menu_item_name, menu_item_options in menu_section.items():
                    callback = None
                    menu_item_description = None
                    wx_id = None
                    if callable(menu_item_options):
                        callback = menu_item_options
                    elif isinstance(menu_item_options, tuple):
                        if len(menu_item_options) >= 1:
                            callback = menu_item_options[0]
                        if len(menu_item_options) >= 2:
                            menu_item_description = menu_item_options[1]
                        if len(menu_item_options) >= 3:
                            wx_id = menu_item_options[2]
                    else:
                        continue

                    if not menu_item_description:
                        menu_item_description = ""
                    if not wx_id:
                        wx_id = wx.ID_ANY

                    menu_item: wx.MenuItem = menu.Append(
                        wx_id, menu_item_name, menu_item_description
                    )
                    self.Bind(wx.EVT_MENU, callback, menu_item)
            menu_bar.Append(menu, menu_name)
        self.SetMenuBar(menu_bar)

    def _edit_preferences(self):
        edit_config: dict = config.get(EDIT_CONFIG_ID, {})
        recent_worlds_limit = (
            edit_config.get("options", {}).get(
                "recent_worlds_limit", DEFAULT_RECENT_WORLDS_LIMIT
            )
        )
        if not isinstance(recent_worlds_limit, int) or recent_worlds_limit < 1:
            recent_worlds_limit = DEFAULT_RECENT_WORLDS_LIMIT

        dialog = SimpleDialog(self, "Preferences")
        sizer = wx.FlexGridSizer(1, 2, 0, 0)
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

        dialog.Fit()

        if dialog.ShowModal() == wx.ID_OK:
            edit_config.setdefault("options", {})
            edit_config["options"]["recent_worlds_limit"] = (
                recent_worlds_limit_ui.GetValue()
            )
            config.put(EDIT_CONFIG_ID, edit_config)


class AmuletLevelNotebook(flatnotebook.FlatNotebook):
    """A notebook to hold all world tabs."""

    # The main menu tab
    _main_menu: AmuletMainMenu

    # The world selector tab (if open)
    _world_selector: WorldSelectPageUI | None

    # The backups tab (if open)
    _backups_page: BackupsPageUI | None

    # Storage of open world tabs for easy lookup
    _open_worlds: Dict[str, CLOSEABLE_PAGE_TYPE]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.Bind(flatnotebook.EVT_FLATNOTEBOOK_PAGE_CLOSING, self._on_page_closing)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self._page_changing, self)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._page_changed, self)

        self._main_menu = AmuletMainMenu(self)
        self._world_selector = None
        self._backups_page = None
        self._delete_page = None
        self._open_worlds = {}
        self._force_quit_without_save = False

    def init(self):
        self._add_world_tab(self._main_menu, lang.get("main_menu.tab_name"))

    def open_level(self, path: str):
        """Open a world panel add it to the notebook"""
        if path in self._open_worlds:
            self.SetSelection(self.GetPageIndex(self._open_worlds[path]))
        else:
            try:
                world = WorldPageUI(self, path)
            except LoaderNoneMatched as e:
                log.error(f"Could not find a loader for this world.\n{e}")
                wx.MessageBox(f"{lang.get('select_world.no_loader_found')}\n{e}")
            except Exception as e:
                error_text = str(e)
                locked_world_error = (
                    "LevelDBException" in type(e).__name__
                    or "db/CURRENT" in error_text
                ) and "being used by another process" in error_text

                if locked_world_error:
                    wx.MessageBox(
                        "This Bedrock world is currently in use by another process.\n\n"
                        "Close Minecraft Bedrock (and any sync/backup/indexing tools using that folder), "
                        "then try opening the world again.",
                        "World Database Locked",
                        style=wx.OK | wx.ICON_WARNING,
                    )
                    return

                log.error(lang.get("select_world.loading_world_failed"), exc_info=True)
                dialog = TracebackDialog(
                    self,
                    lang.get("select_world.loading_world_failed"),
                    str(e),
                    traceback.format_exc(),
                )
                dialog.ShowModal()
                dialog.Destroy()
            else:
                self._open_worlds[path] = world
                self._add_world_tab(world, world.world_name)

    def open_world_select_tab(self):
        """Open the world selector as a tab"""
        if self._world_selector is not None:
            # If the tab already exists, just switch to it
            page_index = self.GetPageIndex(self._world_selector)
            if page_index != wx.NOT_FOUND:
                self.SetSelection(page_index)
                return
            else:
                # The tab was closed, so create a new one
                self._world_selector = None

        # Create a new world selector tab
        self._world_selector = WorldSelectPageUI(self)
        self._add_world_tab(self._world_selector, lang.get("select_world.title"))

    def close_world_select_tab(self):
        """Close the world selector tab if it is open."""
        if self._world_selector is None:
            return

        page_index = self.GetPageIndex(self._world_selector)
        if page_index != wx.NOT_FOUND:
            self.DeletePage(page_index)
        self._world_selector = None

    def open_backups_tab(self):
        """Open the backups tab."""
        if self._backups_page is not None:
            page_index = self.GetPageIndex(self._backups_page)
            if page_index != wx.NOT_FOUND:
                self.SetSelection(page_index)
                return
            self._backups_page = None

        self._backups_page = BackupsPageUI(self)
        self._add_world_tab(self._backups_page, "Backups")

    def close_backups_tab(self):
        """Close the backups tab if it is open."""
        if self._backups_page is None:
            return

        page_index = self.GetPageIndex(self._backups_page)
        if page_index != wx.NOT_FOUND:
            self.DeletePage(page_index)
        self._backups_page = None

    def open_delete_tab(self):
        """Open the delete worlds tab."""
        if self._delete_page is not None:
            page_index = self.GetPageIndex(self._delete_page)
            if page_index != wx.NOT_FOUND:
                self.SetSelection(page_index)
                return
            self._delete_page = None

        self._delete_page = DeletePageUI(self)
        self._add_world_tab(self._delete_page, "Delete Worlds")

    def close_delete_tab(self):
        """Close the delete worlds tab if it is open."""
        if self._delete_page is None:
            return

        page_index = self.GetPageIndex(self._delete_page)
        if page_index != wx.NOT_FOUND:
            self.DeletePage(page_index)
        self._delete_page = None

    def _add_world_tab(self, page: BasePageUI, obj_name: str):
        """Add a tab and enable it."""
        self.AddPage(page, obj_name, True)
        # Defer the tab-strip fixup so it runs after AddPage's internal
        # Freeze/Thaw and all event handlers have finished.
        wx.CallAfter(self._ensure_tabs_visible)

    def close_level(self, path: str):
        """Close a given world and remove it from the notebook"""
        if path in self._open_worlds:
            world = self._open_worlds[path]
            # note we don't remove it from the dictionary here
            # delete page starts the deletion but it can be vetoed
            # it is deleted from the dictionary in _on_page_closing
            self.DeletePage(self.GetPageIndex(world))

    def _on_page_closing(self, evt: flatnotebook.EVT_FLATNOTEBOOK_PAGE_CLOSING):
        """Handle the page closing."""
        page: CLOSEABLE_PAGE_TYPE = self.GetPage(evt.GetSelection())
        if self._force_quit_without_save:
            if page is self._world_selector:
                self._world_selector = None
            elif page is self._backups_page:
                self._backups_page = None
            elif page is self._delete_page:
                self._delete_page = None
            elif hasattr(page, "path"):
                path = page.path
                try:
                    page.disable()
                except Exception:
                    pass
                try:
                    page.close()
                except Exception:
                    pass
                self._open_worlds.pop(path, None)
            return

        if page is self._main_menu:
            # Don't allow closing the main menu
            evt.Veto()
        elif page is self._world_selector:
            # Allow closing the world selector and clear the reference
            self._world_selector = None
        elif page is self._backups_page:
            self._backups_page = None
        elif page is self._delete_page:
            self._delete_page = None
        elif hasattr(page, 'path'):
            # It's a world page
            if page.can_disable() and page.can_close():
                path = page.path
                page.disable()
                page.close()
                del self._open_worlds[path]
            else:
                evt.Veto()

    def _page_changing(self, evt: wx.BookCtrlEvent):
        old_selection_index = evt.GetOldSelection()
        if old_selection_index != wx.NOT_FOUND:
            old_page = self.GetPage(old_selection_index)
            if old_page is not None and not old_page.can_disable():
                evt.Veto()

    def _page_changed(self, evt: wx.BookCtrlEvent):
        """Handle the page changing."""
        if evt.GetOldSelection() != evt.GetSelection():
            if evt.GetOldSelection() != wx.NOT_FOUND:
                old_page = self.GetPage(evt.GetOldSelection())
                if old_page is not None:
                    old_page.disable()

            if self.GetCurrentPage() is self._main_menu:
                new_style = NOTEBOOK_MENU_STYLE
            else:
                new_style = NOTEBOOK_STYLE

            if self.GetAGWWindowStyleFlag() != new_style:
                self.SetAGWWindowStyleFlag(new_style)

            # Defer the tab-strip visibility fixup until after all
            # pending Freeze/Thaw and event processing completes.
            wx.CallAfter(self._ensure_tabs_visible)

        if self.GetCurrentPage() is not None:
            self.GetCurrentPage().enable()

    def _ensure_tabs_visible(self):
        """Make sure the FlatNotebook tab strip is shown and painted.

        FNB_HIDE_ON_SINGLE_TAB causes the internal PageContainer (_pages)
        to hide itself inside its OnPaint handler when there is only one
        tab.  After a second tab is added, the container may still be
        hidden because the queued Refresh calls were suppressed by the
        Freeze/Thaw cycle in AddPage.  This helper forces the container
        visible and triggers a synchronous repaint.
        """
        if self.GetPageCount() > 1:
            if not self._pages.IsShown():
                self._pages.Show()
            self._mainSizer.Layout()
            self._pages.Refresh()
            self._pages.Update()

    def on_app_close(self, evt: wx.CloseEvent):
        if self._force_quit_without_save:
            for path, page in list(self._open_worlds.items()):
                try:
                    page.disable()
                except Exception:
                    pass
                try:
                    page.close()
                except Exception:
                    pass
                self._open_worlds.pop(path, None)

            if self._world_selector is not None:
                self._world_selector = None

            if self._backups_page is not None:
                self._backups_page = None

            if self._delete_page is not None:
                self._delete_page = None

            evt.Skip()
            return

        for path, page in list(self._open_worlds.items()):
            self.close_level(path)

        # Ignore the world selector page during application close.
        if self._world_selector is not None:
            page_index = self.GetPageIndex(self._world_selector)
            if page_index != wx.NOT_FOUND:
                self.DeletePage(page_index)
            self._world_selector = None

        if self._backups_page is not None:
            page_index = self.GetPageIndex(self._backups_page)
            if page_index != wx.NOT_FOUND:
                self.DeletePage(page_index)
            self._backups_page = None

        if self._delete_page is not None:
            page_index = self.GetPageIndex(self._delete_page)
            if page_index != wx.NOT_FOUND:
                self.DeletePage(page_index)
            self._delete_page = None

        # Only block close if actual world pages are still open.
        if self._open_worlds:
            wx.MessageBox(lang.get("app.world_still_used"))
        else:
            evt.Skip()

    def extend_menu(self, menu_dict: dict) -> dict:
        return self.GetCurrentPage().menu(menu_dict)
