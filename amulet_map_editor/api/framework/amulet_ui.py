from __future__ import annotations
import wx
from wx.lib.agw import flatnotebook
from typing import Dict, Union
import traceback
import logging
import sys

from amulet.api.errors import LoaderNoneMatched
from amulet_map_editor.api.wx.ui.select_world import open_level_from_dialog, WorldSelectPageUI
from amulet_map_editor.api.wx.ui.traceback_dialog import TracebackDialog
from amulet_map_editor import __version__, lang
from amulet_map_editor.api.framework.pages import WorldPageUI
from .pages import AmuletMainMenu, BasePageUI

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

        self.Bind(wx.EVT_CLOSE, self._level_notebook.on_app_close)

    def open_level(self, path: str):
        """Open a level. You should use the method in the app."""
        self._level_notebook.open_level(path)

    def open_world_select_tab(self):
        """Open the world selector as a tab. You should use the method in the app."""
        self._level_notebook.open_world_select_tab()

    def close_level(self, path: str):
        """Close a given level. You should use the method in the app."""
        self._level_notebook.close_level(path)

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
        menu_dict.setdefault(lang.get("menu_bar.file.menu_name"), {}).setdefault(
            "system", {}
        ).setdefault(
            f"&{lang.get('program_3d_edit.menu_bar.file.preferences')}",
            lambda evt: self._edit_preferences(),
        )
        # menu_dict.setdefault(lang.get('menu_bar.file.menu_name'), {}).setdefault('system', {}).setdefault('Create World', lambda: self.world.save())
        menu_dict.setdefault(lang.get("menu_bar.file.menu_name"), {}).setdefault(
            "exit", {}
        ).setdefault(f"&{lang.get('menu_bar.file.quit')}", lambda evt: self.Close())
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

    # Storage of open world tabs for easy lookup
    _open_worlds: Dict[str, CLOSEABLE_PAGE_TYPE]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.Bind(flatnotebook.EVT_FLATNOTEBOOK_PAGE_CLOSING, self._on_page_closing)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self._page_changing, self)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._page_changed, self)

        self._main_menu = AmuletMainMenu(self)
        self._world_selector = None
        self._open_worlds = {}

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

    def _add_world_tab(self, page: BasePageUI, obj_name: str):
        """Add a tab and enable it."""
        self.AddPage(page, obj_name, True)

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
        if page is self._main_menu:
            # Don't allow closing the main menu
            evt.Veto()
        elif page is self._world_selector:
            # Allow closing the world selector and clear the reference
            self._world_selector = None
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
                # self.GetPage(evt.GetOldSelection()).disable()
                old_page = self.GetPage(evt.GetOldSelection())
                if old_page is not None:
                    old_page.disable()

            if self.GetCurrentPage() is self._main_menu:
                self.SetAGWWindowStyleFlag(NOTEBOOK_MENU_STYLE)
            else:
                self.SetAGWWindowStyleFlag(NOTEBOOK_STYLE)

        if self.GetCurrentPage() is not None:
            self.GetCurrentPage().enable()

    def on_app_close(self, evt: wx.CloseEvent):
        for path, page in list(self._open_worlds.items()):
            self.close_level(path)
        if self.GetPageCount() > 1:
            wx.MessageBox(lang.get("app.world_still_used"))
        else:
            evt.Skip()

    def extend_menu(self, menu_dict: dict) -> dict:
        return self.GetCurrentPage().menu(menu_dict)
