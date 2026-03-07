import os
import glob
import math
import shutil
import tempfile
import base64
import stat
from sys import platform
from typing import List, Dict, Tuple, Callable, TYPE_CHECKING
import traceback
import logging
import zipfile

import wx

from amulet import load_format
from amulet.api.errors import FormatError

from amulet_map_editor import lang, CONFIG
from amulet_map_editor.api.wx.ui.traceback_dialog import TracebackDialog
from amulet_map_editor.api.wx.util.ui_preferences import preserve_ui_preferences
from amulet_map_editor.api.framework import app
from amulet_map_editor.api.framework.pages.base_page import BasePageUI

if TYPE_CHECKING:
    from amulet.api.wrapper import WorldFormatWrapper

log = logging.getLogger(__name__)

EDIT_CONFIG_ID = "amulet_edit"
DEFAULT_RECENT_WORLDS_LIMIT = 5


def get_recent_worlds_limit() -> int:
    edit_config = CONFIG.get(EDIT_CONFIG_ID, {})
    options = edit_config.get("options", {}) if isinstance(edit_config, dict) else {}
    limit = options.get("recent_worlds_limit", DEFAULT_RECENT_WORLDS_LIMIT)
    if not isinstance(limit, int):
        limit = DEFAULT_RECENT_WORLDS_LIMIT
    return max(1, min(100, limit))


def update_recent_worlds(path: str) -> None:
    """Update and persist MRU ordering when a world is opened."""
    meta: dict = CONFIG.get("amulet_meta", {})
    recent_worlds: list = meta.setdefault("recent_worlds", [])
    recent_worlds_limit = get_recent_worlds_limit()

    while path in recent_worlds:
        recent_worlds.remove(path)
    recent_worlds.insert(0, path)
    while len(recent_worlds) > recent_worlds_limit:
        recent_worlds.pop(recent_worlds_limit)

    CONFIG.put("amulet_meta", meta)


# Windows 	%APPDATA%\.minecraft
# macOS 	~/Library/Application Support/minecraft
# Linux 	~/.minecraft

minecraft_world_paths: list[tuple[str, str]] = []

if platform == "win32":
    minecraft_world_paths.append(
        (
            lang.get("world.java_platform"),
            os.path.join(os.getenv("APPDATA"), ".minecraft", "saves"),
        )
    )
    minecraft_world_paths.append(
        (
            lang.get("world.bedrock_uwp"),
            os.path.join(
                os.getenv("LOCALAPPDATA"),
                "Packages",
                "Microsoft.MinecraftUWP_8wekyb3d8bbwe",
                "LocalState",
                "games",
                "com.mojang",
                "minecraftWorlds",
            ),
        )
    )
    minecraft_world_paths.append(
        (
            lang.get("world.bedrock_uwp_beta"),
            os.path.join(
                os.getenv("LOCALAPPDATA"),
                "Packages",
                "Microsoft.MinecraftWindowsBeta_8wekyb3d8bbwe",
                "LocalState",
                "games",
                "com.mojang",
                "minecraftWorlds",
            ),
        )
    )
    minecraft_world_paths.append(
        (
            lang.get("world.bedrock_education_store"),
            os.path.join(
                os.getenv("LOCALAPPDATA"),
                "Packages",
                "Microsoft.MinecraftEducationEdition_8wekyb3d8bbwe",
                "LocalState",
                "games",
                "com.mojang",
                "minecraftWorlds",
            ),
        )
    )
    minecraft_world_paths.append(
        (
            lang.get("world.bedrock_education_desktop"),
            os.path.join(
                os.getenv("APPDATA"),
                "Minecraft Education Edition",
                "games",
                "com.mojang",
                "minecraftWorlds",
            ),
        )
    )
    minecraft_world_paths.append(
        (
            lang.get("world.bedrock_netease"),
            os.path.join(
                os.getenv("APPDATA"),
                "MinecraftPE_Netease",
                "minecraftWorlds",
            ),
        )
    )
    for group, key in (
        ("Minecraft Bedrock", "world.bedrock_gdk"),
        ("Minecraft Bedrock Preview", "world.bedrock_gdk_preview"),
    ):
        for worlds_path in glob.glob(
            os.path.join(
                glob.escape(os.getenv("APPDATA")),
                group,
                "Users",
                "*",
                "games",
                "com.mojang",
                "minecraftWorlds",
            )
        ):
            user_id = worlds_path.split(os.sep)[-4]
            minecraft_world_paths.append(
                (
                    f"{lang.get(key)} {user_id}",
                    worlds_path,
                )
            )

elif platform == "darwin":
    minecraft_world_paths.append(
        (
            lang.get("world.java_platform"),
            os.path.join(
                os.path.expanduser("~"),
                "Library",
                "Application Support",
                "minecraft",
                "saves",
            ),
        )
    )
    minecraft_world_paths.append(
        (
            lang.get("world.pocket_platform"),
            os.path.join(
                os.path.expanduser("~"),
                "Library",
                "Application Support",
                "minecraftpe",
                "games",
                "com.mojang",
                "minecraftWorlds",
            ),
        )
    )
elif platform == "linux":
    minecraft_world_paths.append(
        (
            lang.get("world.java_platform"),
            os.path.join(os.path.expanduser("~"), ".minecraft", "saves"),
        )
    )

world_images: Dict[str, Tuple[int, wx.Bitmap, int]] = {}


def _mcworld_search_dirs() -> list[str]:
    """Directories scanned for .mcworld files."""
    home_dir = os.path.expanduser("~")
    search_dirs = [
        home_dir,
        os.path.join(home_dir, "Downloads"),
        os.path.join(home_dir, "Documents"),
    ]

    for _, directory in minecraft_world_paths:
        if os.path.isdir(directory):
            parent_dir = os.path.dirname(directory)
            if parent_dir and os.path.isdir(parent_dir):
                search_dirs.append(parent_dir)

    # Preserve insertion order while removing duplicates.
    return [path for path in dict.fromkeys(search_dirs) if os.path.isdir(path)]


def get_world_image(image_path: str) -> Tuple[wx.Bitmap, int]:
    if (
        image_path not in world_images
        or world_images[image_path][0] != os.stat(image_path)[8]
    ):
        img = wx.Image(image_path, wx.BITMAP_TYPE_ANY)
        width = min(int((img.GetWidth() / img.GetHeight()) * 128), 300)

        world_images[image_path] = (
            os.stat(image_path)[8],
            img.Scale(width, 128, wx.IMAGE_QUALITY_NEAREST).ConvertToBitmap(),
            width,
        )

    return world_images[image_path][1:3]


class WorldUI(wx.Panel):
    """A Panel UI element with the world image, name and description"""

    def __init__(self, parent: wx.Window, world_format: "WorldFormatWrapper"):
        super().__init__(parent, style=wx.TAB_TRAVERSAL | wx.BORDER_RAISED)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(sizer)

        img, width = get_world_image(world_format.world_image_path)

        self.img = wx.StaticBitmap(self, wx.ID_ANY, img, (0, 0), (width, 128))
        sizer.Add(self.img)

        self.world_name = wx.StaticText(
            self,
            label="\n".join(
                [
                    world_format.level_name,
                    world_format.game_version_string,
                    os.path.join(
                        *os.path.normpath(world_format.path).split(os.sep)[-3:]
                    ),
                ]
            ),
        )
        sizer.Add(self.world_name, 0, wx.ALL | wx.ALIGN_CENTER, 5)


class WorldUIButton(WorldUI):
    """A Panel UI element that behaves like a button with the world image, name and description"""

    def __init__(
        self,
        parent: wx.Window,
        world_format: "WorldFormatWrapper",
        open_world_callback,
    ):
        super().__init__(parent, world_format)
        self.path = world_format.path
        self.open_world_callback = open_world_callback
        self._is_hovered = False
        self._is_selected = False

        self._default_bg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
        self._default_fg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
        self._focus_bg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
        self._focus_fg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT)
        self._hover_bg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT)

        self.SetBackgroundColour(self._default_bg)
        self.world_name.SetForegroundColour(self._default_fg)
        self._apply_visual_state()

        self.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.img.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.world_name.Bind(wx.EVT_LEFT_DOWN, self._on_left_down)
        self.Bind(wx.EVT_LEFT_UP, self._call_callback)
        self.img.Bind(wx.EVT_LEFT_UP, self._call_callback)
        self.world_name.Bind(wx.EVT_LEFT_UP, self._call_callback)

        self.Bind(wx.EVT_ENTER_WINDOW, self._on_enter_window)
        self.img.Bind(wx.EVT_ENTER_WINDOW, self._on_enter_window)
        self.world_name.Bind(wx.EVT_ENTER_WINDOW, self._on_enter_window)
        self.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave_window)
        self.img.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave_window)
        self.world_name.Bind(wx.EVT_LEAVE_WINDOW, self._on_leave_window)

    def AcceptsFocus(self) -> bool:
        return True

    def AcceptsFocusFromKeyboard(self) -> bool:
        # Don't accept focus from Tab key - parent WorldList handles that
        return False

    def set_selected(self, selected: bool):
        """Set the visual selection state of this button."""
        self._is_selected = selected
        self._apply_visual_state()

    def is_selected(self) -> bool:
        """Check if this button is currently selected."""
        return self._is_selected

    def _on_enter_window(self, evt: wx.MouseEvent):
        self._is_hovered = True
        self._apply_visual_state()
        evt.Skip()

    def _on_leave_window(self, evt: wx.MouseEvent):
        self._is_hovered = False
        self._apply_visual_state()
        evt.Skip()

    def _on_left_down(self, evt: wx.MouseEvent):
        # Notify parent WorldList to select this button and set focus
        world_list = self.GetParent()
        if isinstance(world_list, WorldList):
            world_list.select_world_by_button(self)
            world_list.SetFocus()
        evt.Skip()

    def _apply_visual_state(self):
        if self._is_selected:
            bg = self._focus_bg
            fg = self._focus_fg
        elif self._is_hovered:
            bg = self._hover_bg
            fg = self._default_fg
        else:
            bg = self._default_bg
            fg = self._default_fg

        self.SetBackgroundColour(bg)
        self.world_name.SetForegroundColour(fg)
        self.Refresh()

    def _call_callback(self, evt):
        self.open_world_callback(self.path)


class WorldList(wx.Panel):
    """A Panel containing zero or more `WorldUIButton`s.
    
    Acts as a single component for Tab navigation, with arrow keys
    navigating between individual world buttons.
    """

    def __init__(self, parent: wx.Window, world_dirs, open_world_callback, sort=True):
        super().__init__(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        self.worlds = []
        self._selected_index = 0
        self._open_world_callback = open_world_callback

        world_formats = []
        for world_path in world_dirs:
            if os.path.isdir(world_path):
                try:
                    world_formats.append(load_format(world_path))
                except FormatError as e:
                    log.info(f"Could not find loader for {world_path} {e}")
                except Exception:
                    log.error(
                        f"Error loading format wrapper for {world_path} {traceback.format_exc()}"
                    )
        if sort:
            world_formats = reversed(sorted(world_formats, key=lambda f: f.last_played))

        for world_format in world_formats:
            try:
                world_button = WorldUIButton(self, world_format, open_world_callback)
                sizer.Add(
                    world_button, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.EXPAND, 5
                )
                self.worlds.append(world_button)
            except Exception as e:
                log.info(f"Failed to display world button for {world_format.path} {e}")

        # Set up keyboard handling
        self.Bind(wx.EVT_SET_FOCUS, self._on_set_focus)
        self.Bind(wx.EVT_KILL_FOCUS, self._on_kill_focus)
        self.Bind(wx.EVT_KEY_DOWN, self._on_key_down)
        self.Bind(wx.EVT_CHAR_HOOK, self._on_key_down)

        # Initialize with first item selected if any worlds exist
        if self.worlds:
            self.worlds[0].set_selected(True)

        self.Layout()

    def AcceptsFocus(self) -> bool:
        return len(self.worlds) > 0

    def AcceptsFocusFromKeyboard(self) -> bool:
        return len(self.worlds) > 0

    def select_world_by_button(self, button: WorldUIButton):
        """Select a world by its button reference."""
        if button in self.worlds:
            self._set_selection(self.worlds.index(button))

    def _set_selection(self, index: int):
        """Set the selected world index and update visual state."""
        if not self.worlds or index < 0 or index >= len(self.worlds):
            return

        # Clear previous selection
        if 0 <= self._selected_index < len(self.worlds):
            self.worlds[self._selected_index].set_selected(False)

        # Set new selection
        self._selected_index = index
        self.worlds[self._selected_index].set_selected(True)
        self._scroll_selected_into_view()

    def _scroll_selected_into_view(self):
        """Ensure the selected item is visible within an ancestor scrolled window."""
        if not self.worlds or not (0 <= self._selected_index < len(self.worlds)):
            return

        scrolled_parent = self.GetParent()
        while scrolled_parent is not None and not isinstance(
            scrolled_parent, wx.ScrolledWindow
        ):
            scrolled_parent = scrolled_parent.GetParent()

        if not isinstance(scrolled_parent, wx.ScrolledWindow):
            return

        selected_world = self.worlds[self._selected_index]

        # Prefer native helper where available.
        if hasattr(scrolled_parent, "ScrollChildIntoView"):
            try:
                scrolled_parent.ScrollChildIntoView(selected_world)
                # Some wx builds only partially scroll; keep a robust fallback below.
            except Exception:
                pass

        y_pixels_per_unit = scrolled_parent.GetScrollPixelsPerUnit()[1]
        if y_pixels_per_unit <= 0:
            return

        item_rect = selected_world.GetScreenRect()
        view_rect = scrolled_parent.GetScreenRect()

        scroll_delta_pixels = 0
        if item_rect.GetTop() < view_rect.GetTop():
            scroll_delta_pixels = item_rect.GetTop() - view_rect.GetTop()
        elif item_rect.GetBottom() > view_rect.GetBottom():
            scroll_delta_pixels = item_rect.GetBottom() - view_rect.GetBottom()
        else:
            return

        current_x_units, current_y_units = scrolled_parent.GetViewStart()
        if scroll_delta_pixels < 0:
            delta_units = math.floor(scroll_delta_pixels / y_pixels_per_unit)
        else:
            delta_units = math.ceil(scroll_delta_pixels / y_pixels_per_unit)

        target_y_units = max(0, current_y_units + int(delta_units))
        scrolled_parent.Scroll(current_x_units, target_y_units)

    def _on_set_focus(self, evt: wx.FocusEvent):
        """When the list gains focus, show the selected item."""
        if self.worlds and 0 <= self._selected_index < len(self.worlds):
            self.worlds[self._selected_index].set_selected(True)
            self._scroll_selected_into_view()
        evt.Skip()

    def _on_kill_focus(self, evt: wx.FocusEvent):
        """When the list loses focus, keep selection visible."""
        # Keep the selection visible even when focus is lost
        evt.Skip()

    def _on_key_down(self, evt: wx.KeyEvent):
        """Handle keyboard navigation within the list."""
        if not self.worlds:
            evt.Skip()
            return

        key_code = evt.GetKeyCode()

        if key_code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER, wx.WXK_SPACE):
            # Activate the selected world
            if 0 <= self._selected_index < len(self.worlds):
                self._open_world_callback(self.worlds[self._selected_index].path)
            return  # Consume the event
        elif key_code in (wx.WXK_UP, wx.WXK_NUMPAD_UP):
            # Move selection up
            new_index = max(0, self._selected_index - 1)
            self._set_selection(new_index)
            return  # Consume the event
        elif key_code in (wx.WXK_DOWN, wx.WXK_NUMPAD_DOWN):
            # Move selection down
            new_index = min(len(self.worlds) - 1, self._selected_index + 1)
            self._set_selection(new_index)
            return  # Consume the event
        elif key_code == wx.WXK_TAB:
            # Let Tab navigate out of the list
            direction = (
                wx.NavigationKeyEvent.IsBackward
                if evt.ShiftDown()
                else wx.NavigationKeyEvent.IsForward
            )
            self.Navigate(direction)
            return  # Consume the event

        evt.Skip()


class CollapsibleWorldListUI(wx.CollapsiblePane):
    """a drop down list of `WorldUIButton`s for a given directory"""

    def __init__(self, parent, paths: List[str], group_name: str, open_world_callback):
        super().__init__(parent, label=group_name)
        self.parent = parent
        self.Bind(wx.EVT_COLLAPSIBLEPANE_CHANGED, self.eval_layout)

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)

        panel = self.GetPane()
        panel.sizer = wx.BoxSizer(wx.VERTICAL)
        panel.SetSizer(panel.sizer)
        self.world_list = WorldList(panel, paths, open_world_callback)
        panel.sizer.Add(self.world_list, 0, wx.EXPAND)

    def eval_layout(self, evt):
        self.Layout()
        self.parent.FitInside()
        evt.Skip()


class ScrollableWorldsUI(wx.Panel):
    # A tree view of all detected worlds grouped by platform and source.
    def __init__(self, parent, open_world_callback):
        super().__init__(parent)
        self.open_world_callback = open_world_callback

        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self._sizer)

        # Add title row for the found worlds tree with right-aligned refresh button
        found_header_sizer = wx.BoxSizer(wx.HORIZONTAL)
        found_worlds_label = wx.StaticText(
            self, label=lang.get("select_world.discovered_worlds")
        )
        found_header_sizer.Add(found_worlds_label, 0, wx.ALIGN_CENTER_VERTICAL)
        found_header_sizer.AddStretchSpacer()

        refresh_button = wx.Button(self, label="Refresh")
        refresh_button.Bind(wx.EVT_BUTTON, self._on_refresh_click)
        found_header_sizer.Add(refresh_button, 0, wx.ALIGN_CENTER_VERTICAL)

        self._sizer.Add(
            found_header_sizer,
            0,
            wx.EXPAND | wx.LEFT | wx.TOP | wx.RIGHT | wx.BOTTOM,
            5,
        )

        self._tree = wx.TreeCtrl(
            self,
            style=wx.TR_HAS_BUTTONS
            | wx.TR_HIDE_ROOT
            | wx.TR_LINES_AT_ROOT
            | wx.TR_SINGLE,
        )
        self._sizer.Add(self._tree, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)

        # Add title for the worlds directory list below the discovered tree.
        title_label = wx.StaticText(self, label=lang.get("select_world.looking_for_worlds_in"))
        self._sizer.Add(title_label, 0, wx.LEFT | wx.TOP | wx.RIGHT, 5)

        # Add readonly text field showing the paths being searched.
        self._path_text = wx.TextCtrl(
            self,
            value="",
            style=wx.TE_READONLY | wx.TE_MULTILINE | wx.BORDER_SIMPLE,
        )
        self._path_text.SetMinSize((-1, 220))
        self._path_text.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))
        self._sizer.Add(self._path_text, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        self._tree.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self._on_item_activated)
        self._tree.Bind(wx.EVT_TREE_KEY_DOWN, self._on_tree_key_down)
        self._tree.Bind(wx.EVT_RIGHT_DOWN, self._on_tree_right_click)

        self.reload()

    @staticmethod
    def _platform_group(directory: str) -> str:
        directory_lower = directory.replace("\\", "/").lower()
        if directory_lower.endswith("/.minecraft/saves"):
            return "Java"
        if "minecraftworlds" in directory_lower:
            return "Bedrock"
        return "Other"

    def _get_selected_world_path(self) -> str | None:
        item = self._tree.GetSelection()
        if not item.IsOk():
            return None
        path = self._tree.GetItemData(item)
        if isinstance(path, str):
            return path
        return None

    def _on_tree_key_down(self, evt: wx.TreeEvent):
        key_code = evt.GetKeyCode()
        if key_code in (wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER, wx.WXK_SPACE):
            path = self._get_selected_world_path()
            if isinstance(path, str):
                self.open_world_callback(path)
                return
        evt.Skip()

    def _on_refresh_click(self, evt):
        """Handle refresh button click."""
        self.reload()

    def _update_tree_height(self):
        """Size the discovered tree to the discovered content height."""
        root = self._tree.GetRootItem()
        if not root.IsOk():
            return

        def count_world_items(item: wx.TreeItemId) -> int:
            count = 0
            if item.IsOk():
                item_data = self._tree.GetItemData(item)
                if isinstance(item_data, str):
                    count += 1

                child, cookie = self._tree.GetFirstChild(item)
                while child.IsOk():
                    count += count_world_items(child)
                    child, cookie = self._tree.GetNextChild(item, cookie)
            return count

        world_count = count_world_items(root)
        row_height = max(18, self._tree.GetCharHeight() + 6)
        # Include room for group rows and a little padding.
        visible_rows = max(6, world_count + 4)
        tree_height = min(700, visible_rows * row_height)
        self._tree.SetMinSize((-1, tree_height))

    def _highlight_world_by_path(self, world_path: str):
        """Find and select a world in the tree by its path."""
        root = self._tree.GetRootItem()
        if not root.IsOk():
            return
        
        def search_tree(item):
            if item.IsOk():
                item_data = self._tree.GetItemData(item)
                if item_data == world_path:
                    self._tree.SelectItem(item)
                    self._tree.ScrollTo(item)
                    return
                
                child, cookie = self._tree.GetFirstChild(item)
                while child.IsOk():
                    search_tree(child)
                    child, cookie = self._tree.GetNextChild(item, cookie)
        
        child, cookie = self._tree.GetFirstChild(root)
        while child.IsOk():
            search_tree(child)
            child, cookie = self._tree.GetNextChild(root, cookie)

    def _on_item_activated(self, evt: wx.TreeEvent):
        """Handle double-click on tree items to open worlds."""
        path = self._tree.GetItemData(evt.GetItem())
        if isinstance(path, str):
            # Check if it's an mcworld file
            if path.lower().endswith('.mcworld'):
                self._open_mcworld_file(path)
            else:
                self.open_world_callback(path)

    def _on_tree_right_click(self, evt: wx.MouseEvent):
        """Handle right-click on tree items to show context menu."""
        pt = evt.GetPosition()
        item, flags = self._tree.HitTest(pt)
        if not item.IsOk():
            return
        
        # Select the item that was right-clicked
        self._tree.SelectItem(item)
        
        # Get the world path from the item
        path = self._tree.GetItemData(item)
        if not isinstance(path, str):
            return
        
        # Check if it's an mcworld file
        is_mcworld = path.lower().endswith('.mcworld')
        
        # Create and show context menu
        menu = wx.Menu()
        open_id = wx.NewIdRef()
        save_as_id = wx.NewIdRef()
        delete_id = wx.NewIdRef()
        
        menu.Append(open_id, "Open")
        menu.Append(save_as_id, "Save As")
        menu.AppendSeparator()
        menu.Append(delete_id, "Delete")
        
        if is_mcworld:
            menu.Bind(wx.EVT_MENU, lambda e: self._open_mcworld_file(path), id=open_id)
            menu.Bind(wx.EVT_MENU, lambda e: self._save_mcworld_as(path), id=save_as_id)
            menu.Bind(wx.EVT_MENU, lambda e: self._delete_world(path), id=delete_id)
        else:
            menu.Bind(wx.EVT_MENU, lambda e: self.open_world_callback(path), id=open_id)
            menu.Bind(wx.EVT_MENU, lambda e: self._save_world_as(path), id=save_as_id)
            menu.Bind(wx.EVT_MENU, lambda e: self._delete_world(path), id=delete_id)
        
        self._tree.PopupMenu(menu, pt)
        menu.Destroy()

    def _save_world_as(self, world_path: str):
        """Handle Save As action for a world."""
        try:
            # Load the world format to get metadata
            world_format = load_format(world_path)
            original_level_name = world_format.level_name
            is_bedrock = world_format.platform == "bedrock"
            
            # Step 1: Show dialog with level name + format choice
            dialog = wx.Dialog(None, title="Save World As", style=wx.DEFAULT_DIALOG_STYLE)
            sizer = wx.BoxSizer(wx.VERTICAL)
            
            sizer.Add(
                wx.StaticText(dialog, label="Level name:"),
                0, wx.LEFT | wx.RIGHT | wx.TOP, 10,
            )
            name_ctrl = wx.TextCtrl(dialog, value=original_level_name)
            sizer.Add(name_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
            
            sizer.Add(
                wx.StaticText(dialog, label="Save format:"),
                0, wx.LEFT | wx.RIGHT | wx.TOP, 10,
            )
            rb_folder = wx.RadioButton(
                dialog, label="World directory", style=wx.RB_GROUP,
            )
            rb_mcworld = wx.RadioButton(dialog, label=".mcworld file")
            sizer.Add(rb_folder, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
            sizer.Add(rb_mcworld, 0, wx.LEFT | wx.RIGHT, 10)
            
            # Default to directory format
            rb_folder.SetValue(True)
            
            btn_sizer = dialog.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
            sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)
            dialog.SetSizer(sizer)
            sizer.Fit(dialog)
            
            name_ctrl.SetFocus()
            name_ctrl.SelectAll()
            
            if dialog.ShowModal() != wx.ID_OK:
                dialog.Destroy()
                return
            
            new_level_name = name_ctrl.GetValue().strip()
            save_as_mcworld = rb_mcworld.GetValue()
            dialog.Destroy()
            
            if not new_level_name:
                wx.LogError("Level name cannot be empty")
                return
            
            # Step 2: Determine destination
            if save_as_mcworld:
                # Ask for file save location
                file_name = new_level_name
                if not file_name.lower().endswith('.mcworld'):
                    file_name += '.mcworld'
                
                file_dialog = wx.FileDialog(
                    None,
                    f"Save world as {file_name}",
                    "",
                    file_name,
                    wildcard="Bedrock world archive (*.mcworld)|*.mcworld",
                    style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                )
                try:
                    if file_dialog.ShowModal() == wx.ID_CANCEL:
                        return
                    save_path = file_dialog.GetPath()
                finally:
                    file_dialog.Destroy()
            else:
                # Save to standard Minecraft world directory
                if is_bedrock:
                    # For Bedrock, generate a random 12-character folder name
                    folder_name = base64.b64encode(os.urandom(8)).decode("ascii")
                    # Use first Bedrock worlds directory found
                    default_dir = None
                    for group_name, directory in minecraft_world_paths:
                        if "minecraftworlds" in directory.lower() and os.path.isdir(directory):
                            default_dir = directory
                            break
                else:
                    # For Java, use the level name as folder
                    folder_name = new_level_name
                    # Use Java saves directory
                    default_dir = None
                    for group_name, directory in minecraft_world_paths:
                        if "saves" in directory.lower() and os.path.isdir(directory):
                            default_dir = directory
                            break
                
                # If no standard directory found, ask user
                if not default_dir:
                    dir_dialog = wx.DirDialog(
                        None,
                        f"Select where to save world folder '{folder_name}'",
                        "",
                        wx.DD_DEFAULT_STYLE,
                    )
                    try:
                        if dir_dialog.ShowModal() == wx.ID_CANCEL:
                            return
                        default_dir = dir_dialog.GetPath()
                    finally:
                        dir_dialog.Destroy()
                
                save_path = os.path.join(default_dir, folder_name)
                
                # Check if destination already exists
                if os.path.exists(save_path):
                    wx.LogError(f"A world already exists at this location")
                    return
            
            # Step 3: Copy and save the world
            busy_msg = wx.BusyInfo("Saving world...")
            try:
                if save_as_mcworld:
                    # Create a temporary directory for the world structure
                    temp_dir = tempfile.mkdtemp(prefix="amulet_saveas_")
                    try:
                        # Copy all files from source to temp
                        for item in os.listdir(world_path):
                            src_path = os.path.join(world_path, item)
                            dst_path = os.path.join(temp_dir, item)
                            if os.path.isdir(src_path):
                                shutil.copytree(src_path, dst_path)
                            else:
                                shutil.copy2(src_path, dst_path)
                        
                        # Write level name into the temp copy before zipping
                        self._write_level_name(temp_dir, new_level_name)
                        
                        # Create zip file from temp directory
                        with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                            for root, dirs, files in os.walk(temp_dir):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    arcname = os.path.relpath(file_path, temp_dir)
                                    zf.write(file_path, arcname)
                    finally:
                        # Clean up temp directory
                        shutil.rmtree(temp_dir)
                else:
                    # Create directory and copy world
                    os.makedirs(save_path, exist_ok=True)
                    
                    # Copy all files from source
                    for item in os.listdir(world_path):
                        src_path = os.path.join(world_path, item)
                        dst_path = os.path.join(save_path, item)
                        if os.path.isdir(src_path):
                            shutil.copytree(src_path, dst_path)
                        else:
                            shutil.copy2(src_path, dst_path)
                    
                    # Write level name into the copied world
                    self._write_level_name(save_path, new_level_name)
            finally:
                del busy_msg
            
            # Refresh the worlds list and highlight the newly saved world
            self.reload()
            self._highlight_world_by_path(save_path)
        except Exception as e:
            log.error(f"Error saving world as: {e}")
            wx.LogError("Failed to save world")

    @staticmethod
    def _write_level_name(world_dir: str, level_name: str):
        """Write the level name into the world's metadata files.
        
        Opens the world format, sets level_name, saves (writes level.dat 
        and levelname.txt), then closes.
        """
        try:
            fmt = load_format(world_dir)
            fmt.open()
            try:
                fmt.level_name = level_name
                fmt.save()
            finally:
                fmt.close()
        except Exception as e:
            log.warning(f"Could not update level name via format: {e}")
            # Fallback: write levelname.txt directly
            try:
                with open(os.path.join(world_dir, "levelname.txt"), "w", encoding="utf-8") as f:
                    f.write(level_name)
            except Exception as e2:
                log.debug(f"Could not write levelname.txt fallback: {e2}")

    def _add_mcworld_files_to_tree(self, root: wx.TreeItemId):
        """Scan for and add .mcworld files to the tree."""
        mcworld_files = []
        search_dirs = _mcworld_search_dirs()
        
        # Search for mcworld files at the top level of each directory
        for search_dir in search_dirs:
            if os.path.isdir(search_dir):
                try:
                    for file_path in glob.glob(os.path.join(glob.escape(search_dir), "*.mcworld")):
                        if os.path.isfile(file_path):
                            mcworld_files.append(file_path)
                except Exception as e:
                    log.debug(f"Error searching {search_dir} for mcworld files: {e}")
        
        # Also search recursively one level deep
        for search_dir in search_dirs:
            if os.path.isdir(search_dir):
                try:
                    for file_path in glob.glob(os.path.join(glob.escape(search_dir), "*", "*.mcworld")):
                        if os.path.isfile(file_path):
                            mcworld_files.append(file_path)
                except Exception as e:
                    log.debug(f"Error recursively searching {search_dir} for mcworld files: {e}")
        
        # Remove duplicates and sort
        mcworld_files = sorted(list(set(mcworld_files)))
        
        if mcworld_files:
            # Create a parent node for mcworld files
            mcworld_node = self._tree.AppendItem(root, "MCWorld Files (.mcworld)")
            
            for mcworld_path in mcworld_files:
                file_name = os.path.basename(mcworld_path)
                mcworld_item = self._tree.AppendItem(mcworld_node, file_name)
                self._tree.SetItemData(mcworld_item, mcworld_path)
            
            self._tree.Expand(mcworld_node)
        else:
            # Log if no mcworld files found (for debugging)
            log.debug(f"No .mcworld files found in search directories: {search_dirs}")

    def _open_mcworld_file(self, mcworld_path: str):
        """Open a .mcworld file by extracting it to a temporary location."""
        try:
            # Create a temporary directory for extraction
            temp_dir = os.path.join(os.path.expanduser("~"), ".amulet_temp_worlds")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Extract the mcworld file
            file_name = os.path.basename(mcworld_path)
            world_name = os.path.splitext(file_name)[0]
            extract_dir = os.path.join(temp_dir, world_name)
            
            # Remove existing extraction if present
            if os.path.exists(extract_dir):
                shutil.rmtree(extract_dir)
            
            os.makedirs(extract_dir)
            
            busy_msg = wx.BusyInfo("Extracting world...")
            try:
                with zipfile.ZipFile(mcworld_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
            finally:
                del busy_msg
            
            # Open the extracted world
            self.open_world_callback(extract_dir)
        except Exception as e:
            log.error(f"Error opening mcworld file: {e}")
            wx.LogError("Failed to open mcworld file")

    def _save_mcworld_as(self, mcworld_path: str):
        """Save a .mcworld file with format choice (directory or .mcworld)."""
        try:
            # Extract the mcworld to a temp directory so we can inspect it
            temp_dir = tempfile.mkdtemp(prefix="amulet_mcworld_saveas_")
            try:
                busy_extract = wx.BusyInfo("Extracting world...")
                try:
                    with zipfile.ZipFile(mcworld_path, 'r') as zip_ref:
                        zip_ref.extractall(temp_dir)
                finally:
                    del busy_extract

                # Load format from extracted world to get metadata
                world_format = load_format(temp_dir)
                original_level_name = world_format.level_name
                is_bedrock = world_format.platform == "bedrock"

                # Show the same format choice dialog as _save_world_as
                dialog = wx.Dialog(None, title="Save World As", style=wx.DEFAULT_DIALOG_STYLE)
                sizer = wx.BoxSizer(wx.VERTICAL)

                sizer.Add(
                    wx.StaticText(dialog, label="Level name:"),
                    0, wx.LEFT | wx.RIGHT | wx.TOP, 10,
                )
                name_ctrl = wx.TextCtrl(dialog, value=original_level_name)
                sizer.Add(name_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

                sizer.Add(
                    wx.StaticText(dialog, label="Save format:"),
                    0, wx.LEFT | wx.RIGHT | wx.TOP, 10,
                )
                rb_folder = wx.RadioButton(
                    dialog, label="World directory", style=wx.RB_GROUP,
                )
                rb_mcworld = wx.RadioButton(dialog, label=".mcworld file")
                sizer.Add(rb_folder, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
                sizer.Add(rb_mcworld, 0, wx.LEFT | wx.RIGHT, 10)

                # Default to .mcworld since the source is a .mcworld
                rb_mcworld.SetValue(True)

                btn_sizer = dialog.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
                sizer.Add(btn_sizer, 0, wx.EXPAND | wx.ALL, 10)
                dialog.SetSizer(sizer)
                sizer.Fit(dialog)

                name_ctrl.SetFocus()
                name_ctrl.SelectAll()

                if dialog.ShowModal() != wx.ID_OK:
                    dialog.Destroy()
                    return

                new_level_name = name_ctrl.GetValue().strip()
                save_as_mcworld = rb_mcworld.GetValue()
                dialog.Destroy()

                if not new_level_name:
                    wx.LogError("Level name cannot be empty")
                    return

                # Determine destination
                if save_as_mcworld:
                    file_name = new_level_name
                    if not file_name.lower().endswith('.mcworld'):
                        file_name += '.mcworld'

                    file_dialog = wx.FileDialog(
                        None,
                        f"Save world as {file_name}",
                        "",
                        file_name,
                        wildcard="Bedrock world archive (*.mcworld)|*.mcworld",
                        style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT,
                    )
                    try:
                        if file_dialog.ShowModal() == wx.ID_CANCEL:
                            return
                        save_path = file_dialog.GetPath()
                    finally:
                        file_dialog.Destroy()
                else:
                    if is_bedrock:
                        folder_name = base64.b64encode(os.urandom(8)).decode("ascii")
                        default_dir = None
                        for group_name, directory in minecraft_world_paths:
                            if "minecraftworlds" in directory.lower() and os.path.isdir(directory):
                                default_dir = directory
                                break
                    else:
                        folder_name = new_level_name
                        default_dir = None
                        for group_name, directory in minecraft_world_paths:
                            if "saves" in directory.lower() and os.path.isdir(directory):
                                default_dir = directory
                                break

                    if not default_dir:
                        dir_dialog = wx.DirDialog(
                            None,
                            f"Select where to save world folder '{folder_name}'",
                            "",
                            wx.DD_DEFAULT_STYLE,
                        )
                        try:
                            if dir_dialog.ShowModal() == wx.ID_CANCEL:
                                return
                            default_dir = dir_dialog.GetPath()
                        finally:
                            dir_dialog.Destroy()

                    save_path = os.path.join(default_dir, folder_name)

                    if os.path.exists(save_path):
                        wx.LogError("A world already exists at this location")
                        return

                # Write level name into the extracted temp copy
                self._write_level_name(temp_dir, new_level_name)

                # Save
                busy_msg = wx.BusyInfo("Saving world...")
                try:
                    if save_as_mcworld:
                        with zipfile.ZipFile(save_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                            for root, dirs, files in os.walk(temp_dir):
                                for file in files:
                                    file_path = os.path.join(root, file)
                                    arcname = os.path.relpath(file_path, temp_dir)
                                    zf.write(file_path, arcname)
                    else:
                        os.makedirs(save_path, exist_ok=True)
                        for item in os.listdir(temp_dir):
                            src_path = os.path.join(temp_dir, item)
                            dst_path = os.path.join(save_path, item)
                            if os.path.isdir(src_path):
                                shutil.copytree(src_path, dst_path)
                            else:
                                shutil.copy2(src_path, dst_path)
                finally:
                    del busy_msg

                self.reload()
                self._highlight_world_by_path(save_path)
            finally:
                # Clean up temp extraction directory
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            log.error(f"Error saving mcworld file as: {e}")
            wx.LogError("Failed to save mcworld file")

    def _delete_world(self, world_path: str):
        """Delete a world after confirming with the user."""
        try:
            def _remove_readonly(func, path, exc_info):
                """Retry remove operations after clearing read-only bit on Windows."""
                try:
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
                except Exception:
                    raise

            def _delete_error_message(exc: Exception, fallback_path: str) -> str:
                """Build a user-friendly delete error, highlighting read-only causes."""
                failed_path = getattr(exc, "filename", None) or fallback_path
                exc_text = str(exc)

                if isinstance(exc, PermissionError):
                    try:
                        if os.path.exists(failed_path):
                            mode = os.stat(failed_path).st_mode
                            is_read_only = (mode & stat.S_IWRITE) == 0
                            if is_read_only or not os.access(failed_path, os.W_OK):
                                return (
                                    "Failed to delete world because a file or folder is read-only. "
                                    "Remove the read-only attribute and try again."
                                )
                    except Exception:
                        pass

                    lowered = exc_text.lower()
                    if "read-only" in lowered or "readonly" in lowered:
                        return (
                            "Failed to delete world because a file or folder is read-only. "
                            "Remove the read-only attribute and try again."
                        )

                return f"Failed to delete world: {exc}"

            # Get the world name for display
            world_name = os.path.basename(world_path.rstrip("\\/")) or world_path
            
            # Show confirmation dialog
            dlg = wx.MessageDialog(
                None,
                f"Are you sure you want to delete '{world_name}'?\n\nThis action cannot be undone.",
                "Delete World",
                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING,
                pos=wx.DefaultPosition
            )
            
            # Set the button labels and make Cancel the default
            dlg.SetYesNoLabels("Yes, I really want to delete this world", "Cancel")
            
            result = dlg.ShowModal()
            dlg.Destroy()
            
            if result != wx.ID_YES:
                return

            if not os.path.exists(world_path):
                wx.LogError("The selected world could not be found.")
                self.reload()
                return

            # Deleting a currently open world on Windows commonly fails due to file locks.
            try:
                level_notebook = app.get_app()._amulet_ui._level_notebook
                if os.path.isdir(world_path) and world_path in level_notebook._open_worlds:
                    wx.LogError("Close this world in the editor before deleting it.")
                    return
            except Exception:
                # If app internals change, skip this optional guard and continue.
                pass
            
            # Delete the world
            if world_path.lower().endswith(".mcworld") or os.path.isfile(world_path):
                # It's an .mcworld file or a direct file path.
                try:
                    os.remove(world_path)
                    log.info(f"Deleted mcworld file: {world_path}")
                except Exception as e:
                    log.error(f"Error deleting mcworld file: {e}")
                    wx.LogError(_delete_error_message(e, world_path))
                    return
            else:
                # It's a directory
                try:
                    shutil.rmtree(world_path, onerror=_remove_readonly)
                    log.info(f"Deleted world directory: {world_path}")
                except Exception as e:
                    log.error(f"Error deleting world directory: {e}")
                    wx.LogError(_delete_error_message(e, world_path))
                    return
            
            # Refresh the worlds list
            self.reload()
        except Exception as e:
            log.error(f"Error in _delete_world: {e}")
            wx.LogError("Failed to delete world")

    def reload(self):
        self._tree.DeleteAllItems()
        root = self._tree.AddRoot("worlds")

        # Update path text field with existing directories and mcworld search locations.
        existing_paths = []
        shown_dirs = set()
        for group_name, directory in minecraft_world_paths:
            if os.path.isdir(directory):
                existing_paths.append(f"{group_name}\n  {directory}")
                shown_dirs.add(directory)

        mcworld_dirs = [d for d in _mcworld_search_dirs() if d not in shown_dirs]
        if mcworld_dirs:
            existing_paths.append(
                f"{lang.get('select_world.mcworld_search_locations')}\n  "
                + "\n  ".join(mcworld_dirs)
            )
        
        if existing_paths:
            self._path_text.SetValue("\n\n".join(existing_paths))
        else:
            self._path_text.SetValue("No world directories found")

        platform_nodes: Dict[str, wx.TreeItemId] = {}
        nested_section_nodes: Dict[Tuple[str, str], wx.TreeItemId] = {}
        subsection_nodes: Dict[Tuple[str, str], wx.TreeItemId] = {}

        for group_name, directory in sorted(minecraft_world_paths, key=lambda x: x[0]):
            if not os.path.isdir(directory):
                continue

            platform_group = self._platform_group(directory)
            tree_platform_group = "Bedrock" if platform_group in {"Bedrock", "Java"} else platform_group

            if tree_platform_group not in platform_nodes:
                platform_nodes[tree_platform_group] = self._tree.AppendItem(root, tree_platform_group)

            subtree_parent = platform_nodes[tree_platform_group]
            if platform_group == "Java":
                nested_section_key = (tree_platform_group, "Java")
                if nested_section_key not in nested_section_nodes:
                    nested_section_nodes[nested_section_key] = self._tree.AppendItem(
                        subtree_parent, "Java"
                    )
                subtree_parent = nested_section_nodes[nested_section_key]

            subsection_key = (tree_platform_group, group_name)
            if subsection_key not in subsection_nodes:
                subsection_nodes[subsection_key] = self._tree.AppendItem(
                    subtree_parent, group_name
                )

            world_formats = []
            for world_path in glob.glob(os.path.join(glob.escape(directory), "*")):
                if os.path.isdir(world_path):
                    try:
                        world_formats.append(load_format(world_path))
                    except FormatError as e:
                        log.info(f"Could not find loader for {world_path} {e}")
                    except Exception:
                        log.error(
                            f"Error loading format wrapper for {world_path} {traceback.format_exc()}"
                        )

            for world_format in sorted(
                world_formats, key=lambda w: w.last_played, reverse=True
            ):
                world_label = f"{world_format.level_name} ({world_format.game_version_string})"
                world_item = self._tree.AppendItem(
                    subsection_nodes[subsection_key], world_label
                )
                self._tree.SetItemData(world_item, world_format.path)

        # Add mcworld files (.mcworld archives)
        self._add_mcworld_files_to_tree(root)

        for platform_node in platform_nodes.values():
            self._tree.Expand(platform_node)
        for nested_node in nested_section_nodes.values():
            self._tree.Expand(nested_node)
        for subsection_node in subsection_nodes.values():
            self._tree.Expand(subsection_node)

        self._update_tree_height()
        self.Layout()


class WorldSelectUI(wx.Panel):
    # a frame containing a refresh button for the UI, a sort order for the worlds
    # and a vertical list of `WorldDirectoryUI`s for each directory
    # perhaps also a select directory option
    def __init__(self, parent, open_world_callback):
        super().__init__(parent)
        self.open_world_callback = open_world_callback

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        header_sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(header_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL)

        self.header_open_world = wx.Button(
            self, label=lang.get("select_world.open_world_button")
        )
        font = self.header_open_world.GetFont()
        font.SetPointSize(16)
        self.header_open_world.SetFont(font)
        self.header_open_world.Bind(wx.EVT_BUTTON, self._open_world)
        header_sizer.Add(self.header_open_world, 0, wx.ALL | wx.CENTER, 5)

        self.header_open_mcworld = wx.Button(
            self, label=lang.get("select_world.open_mcworld_button")
        )
        font = self.header_open_mcworld.GetFont()
        font.SetPointSize(16)
        self.header_open_mcworld.SetFont(font)
        self.header_open_mcworld.Bind(wx.EVT_BUTTON, self._open_mcworld)
        header_sizer.Add(self.header_open_mcworld, 0, wx.ALL | wx.CENTER, 5)

        content = ScrollableWorldsUI(self, open_world_callback)
        sizer.Add(content, 1, wx.EXPAND)

    def _open_world(self, evt):
        dir_dialog = wx.DirDialog(
            None,
            lang.get("select_world.open_world_dialogue"),
            "",
            wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
        )
        try:
            if dir_dialog.ShowModal() == wx.ID_CANCEL:
                return
            path = dir_dialog.GetPath()
        except Exception:
            wx.LogError(lang.get("select_world.select_directory_failed"))
            return
        finally:
            dir_dialog.Destroy()
        self.open_world_callback(path)

    def _open_mcworld(self, evt):
        mcworld_dialog = wx.FileDialog(
            None,
            lang.get("select_world.open_mcworld_dialogue"),
            "",
            style=wx.FD_DEFAULT_STYLE | wx.FD_FILE_MUST_EXIST,
            wildcard="Bedrock world archive (*.mcworld)|*.mcworld",
        )
        try:
            if mcworld_dialog.ShowModal() == wx.ID_CANCEL:
                return
            mcworld_path = mcworld_dialog.GetPath()
        except Exception:
            wx.LogError(lang.get("select_world.select_directory_failed"))
            return
        finally:
            mcworld_dialog.Destroy()

        dir_dialog = wx.DirDialog(
            None,
            lang.get("select_world.extract_mcworld_dialogue"),
            "",
            wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
        )
        try:
            if dir_dialog.ShowModal() == wx.ID_CANCEL:
                return
            extract_dir = dir_dialog.GetPath()
        except Exception:
            wx.LogError(lang.get("select_world.select_directory_failed"))
            return
        finally:
            dir_dialog.Destroy()

        if next(os.scandir(extract_dir), None) is not None:
            wx.LogError(lang.get("select_world.extracting_world_not_empty"))
            return

        busy_msg = wx.BusyInfo(lang.get("select_world.extracting_world_wait"))

        try:
            zipfile.ZipFile(mcworld_path).extractall(extract_dir)
        except Exception as e:
            del busy_msg
            dialog = TracebackDialog(
                self,
                lang.get("select_world.extracting_world_failed"),
                str(e),
                traceback.format_exc(),
            )
            dialog.ShowModal()
            dialog.Destroy()
            return
        else:
            del busy_msg

        wx.MessageBox(lang.get("select_world.extracting_world_finished"), "Info", wx.OK)

        self.open_world_callback(extract_dir)


class RecentWorldUI(wx.ScrolledWindow):
    def __init__(self, parent, open_world_callback):
        super().__init__(parent, style=wx.VSCROLL | wx.TAB_TRAVERSAL)
        self._open_world_callback = open_world_callback
        # Use a practical wheel step while keyboard selection visibility is
        # handled by WorldList._scroll_selected_into_view.
        self.SetScrollRate(0, 20)

        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self._sizer)

        # Title with Clear All button
        title_sizer = wx.BoxSizer(wx.HORIZONTAL)
        text = wx.StaticText(
            self,
            wx.ID_ANY,
            lang.get("select_world.recent_worlds"),
            wx.DefaultPosition,
            wx.DefaultSize,
            0,
        )
        text.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        title_sizer.Add(text, 0, wx.ALL, 5)
        
        title_sizer.AddStretchSpacer(1)
        
        clear_button = wx.Button(self, wx.ID_ANY, lang.get("select_world.clear_all"), size=(80, -1))
        clear_button.Bind(wx.EVT_BUTTON, self._on_clear_all)
        title_sizer.Add(clear_button, 0, wx.ALL, 5)
        
        self._sizer.Add(title_sizer, 0, wx.EXPAND)

        self._world_list = None
        self.rebuild()
    
    def _on_clear_all(self, evt):
        """Clear all recent worlds."""
        meta: dict = CONFIG.get("amulet_meta", {})
        meta["recent_worlds"] = []
        CONFIG.put("amulet_meta", meta)
        self.rebuild()

    def focus_recent_list(self) -> bool:
        """Focus the recent-world list so keyboard navigation works immediately."""
        if self._world_list is not None and self._world_list.AcceptsFocus():
            self._world_list.SetFocus()
            return True
        if self.AcceptsFocus():
            self.SetFocus()
            return True
        return False

    def rebuild(self, new_world: str = None):
        meta: dict = CONFIG.get("amulet_meta", {})
        recent_worlds: list = meta.setdefault("recent_worlds", [])
        if new_world is not None:
            update_recent_worlds(new_world)
            meta = CONFIG.get("amulet_meta", {})
            recent_worlds = meta.setdefault("recent_worlds", [])
        if self._world_list is not None:
            self._world_list.Destroy()
        self._world_list = WorldList(
            self, recent_worlds, self._open_world_callback, sort=False
        )
        self._sizer.Add(self._world_list, 1, wx.EXPAND, 5)
        self.Layout()
        self.FitInside()


class WorldSelectAndRecentUI(wx.Panel):
    def __init__(self, parent, open_world_callback):
        super(WorldSelectAndRecentUI, self).__init__(parent, wx.HORIZONTAL)
        self._open_world_callback = open_world_callback

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        warning_text = wx.StaticText(
            self,
            label=lang.get("select_world.open_world_warning"),
        )
        warning_text.SetFont(wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        sizer.Add(warning_text, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 5)
        # bar

        select_world = WorldSelectUI(self, self._update_recent)
        sizer.Add(select_world, 1, wx.ALL | wx.EXPAND, 5)

    def _update_recent(self, path):
        update_recent_worlds(path)
        self._open_world_callback(path)


@preserve_ui_preferences
class WorldSelectDialog(wx.Dialog):
    def __init__(self, parent: wx.Window, open_world_callback: Callable[[str], None]):
        super().__init__(
            parent,
            title=lang.get("select_world.title"),
            pos=wx.Point(50, 50),
            size=wx.Size(*[int(s * 0.95) for s in parent.GetSize()]),
            style=wx.CAPTION | wx.CLOSE_BOX | wx.MAXIMIZE_BOX
            # | wx.MAXIMIZE
            | wx.SYSTEM_MENU | wx.TAB_TRAVERSAL | wx.CLIP_CHILDREN | wx.RESIZE_BORDER,
        )
        self.Bind(wx.EVT_CLOSE, self._hide_event)

        self._open_world_callback = open_world_callback
        self.world_select = WorldSelectAndRecentUI(self, self._run_callback)

    def _run_callback(self, path):
        self._close()
        self._open_world_callback(path)

    def _hide_event(self, evt):
        self._close()
        evt.Skip()

    def _close(self):
        if self.IsModal():
            self.EndModal(0)
        else:
            self.Close()


class WorldSelectPageUI(wx.Panel, BasePageUI):
    """Page to select and open a world."""

    def __init__(self, parent: wx.Window):
        super().__init__(parent)
        self._parent_notebook = parent
        self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)

        warning_text = wx.StaticText(
            self,
            label=lang.get("select_world.open_world_warning"),
        )
        warning_text.SetFont(wx.Font(20, wx.DEFAULT, wx.NORMAL, wx.NORMAL))
        sizer.Add(warning_text, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 5)

        select_world = WorldSelectUI(self, self._on_world_selected)
        sizer.Add(select_world, 1, wx.ALL | wx.EXPAND, 5)

    def _close_open_world_tab(self):
        """Close the open-world selector tab and return to the previous tab."""
        if hasattr(self._parent_notebook, "close_world_select_tab"):
            self._parent_notebook.close_world_select_tab()

    def _on_char_hook(self, evt: wx.KeyEvent):
        """Allow Esc and Ctrl+Q to cancel the open-world tab."""
        key_code = evt.GetKeyCode()
        if key_code == wx.WXK_ESCAPE:
            self._close_open_world_tab()
            return

        if (
            key_code in (ord("Q"), ord("q"))
            and evt.ControlDown()
            and not evt.ShiftDown()
            and not evt.AltDown()
        ):
            self._close_open_world_tab()
            return

        evt.Skip()

    def enable(self):
        """Run when the tab is shown/enabled. Refresh menu to remove Edit/Camera menus."""
        self.GetTopLevelParent().create_menu()

    def _on_world_selected(self, path):
        """Called when a world is selected. Updates recent worlds and opens the world."""
        update_recent_worlds(path)
        # Open the world (but keep this tab open for management)
        app.open_level(path)


def open_level_from_dialog(parent: wx.Window):
    """Show the open world dialog and open the selected world."""
    select_world = WorldSelectDialog(parent, app.open_level)
    select_world.ShowModal()
    select_world.Destroy()
