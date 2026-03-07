import threading
import os
import base64
import shutil
import zipfile
import tempfile

import wx
from typing import List, Tuple, Type, Union, Optional
import traceback
import importlib
import pkgutil
import logging

from amulet.api.errors import LoaderNoneMatched
from amulet import load_level

from amulet_map_editor import programs, lang
from amulet_map_editor.api.datatypes import MenuData
from amulet_map_editor.api.framework import app
from amulet_map_editor.api.framework.menu_utils import ensure_mnemonic
from amulet_map_editor.api.framework.pages import BasePageUI
from amulet_map_editor.api.framework.programs import BaseProgram, AboutProgram
from amulet_map_editor.api.wx.ui.traceback_dialog import TracebackDialog
from amulet_map_editor.api.wx.ui.selectable_message_dialog import SelectableMessageBox

_extensions: List[Tuple[str, Type[BaseProgram]]] = []
_fixed_extensions: List[Tuple[str, Type[BaseProgram]]] = [
    (lang.get("program_about.tab_name"), AboutProgram)
]

log = logging.getLogger(__name__)


def load_extensions():
    if not _extensions:
        _extensions.extend(_fixed_extensions)

        extensions = []

        for _, module_name, _ in pkgutil.iter_modules(
            programs.__path__, f"{programs.__name__}."
        ):
            extensions.append(load_extension(module_name))

        # Sort with explicit order for known core tabs (About, Viewport, Convert)
        # to maintain consistent positioning regardless of alphabetical name changes.
        def _extension_sort_key(ext):
            name = ext[0]
            # Map known program names to desired order positions
            order_map = {
                lang.get("program_about.tab_name"): 0,
                lang.get("program_3d_edit.tab_name"): 1,  # Viewport
                lang.get("program_convert.tab_name"): 2,
            }
            return (order_map.get(name, 999), name)
        
        _extensions.extend(
            sorted((ext for ext in extensions if ext is not None), key=_extension_sort_key)
        )


def load_extension(
    module_name: str,
) -> Optional[Tuple[str, Union[Type[BaseProgram], Type[wx.Window]]]]:
    # load module and confirm that all required attributes are defined
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        log.warning(f"Failed to import {module_name}.\n{traceback.format_exc()}")
    else:
        if hasattr(module, "export"):
            export = getattr(module, "export")
            if isinstance(export, dict):
                ui = export.get("ui", None)
                name = export.get("name", None)
                if (
                    isinstance(name, str)
                    and issubclass(ui, BaseProgram)
                    and issubclass(ui, wx.Window)
                ):
                    return name, ui


class WorldPageUI(wx.Notebook, BasePageUI):
    def __init__(self, parent: wx.Window, path: str):
        super().__init__(parent, style=wx.NB_LEFT)
        self._path = path
        self._base_tab_labels: dict[int, str] = {}
        try:
            self.world = load_level(path)
        except LoaderNoneMatched as e:
            self.Destroy()
            raise e
        self.world_name = self.world.level_wrapper.level_name
        self._load_extensions()
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGING, self._page_changing, self)
        self.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self._page_changed, self)
        wx.CallAfter(self._refresh_tab_highlight)

    @staticmethod
    def _strip_tab_prefix(label: str) -> str:
        if label.startswith("> ") or label.startswith("  "):
            return label[2:]
        return label

    def _refresh_tab_highlight(self):
        """Apply explicit selected-tab emphasis for vertical tabs."""
        selected = self.GetSelection()
        if selected == wx.NOT_FOUND:
            return

        for index in range(self.GetPageCount()):
            base_label = self._base_tab_labels.get(
                index, self._strip_tab_prefix(self.GetPageText(index))
            )
            if index == selected:
                # wx.Notebook does not support per-tab font weight on all platforms.
                # Use uppercase + marker to create a bold-like active emphasis.
                self.SetPageText(index, f"> {base_label.upper()}")
            else:
                self.SetPageText(index, f"  {base_label}")

        self.Refresh()

    def GetPage(self, page) -> BaseProgram:
        wx_page = super().GetPage(page)
        if not isinstance(wx_page, BaseProgram):
            raise Exception("GetPage did not return BaseProgram instance.")
        return wx_page

    @property
    def path(self) -> str:
        return self._path

    def menu(self, menu: MenuData) -> MenuData:
        menu.setdefault(lang.get("menu_bar.file.menu_name"), {}).setdefault(
            "system", {}
        ).setdefault(
            f"{ensure_mnemonic(lang.get('action.act_save_as').replace('&', ''), 'a')}\tCtrl+Shift+S",
            lambda evt: self._save_as(),
        )
        menu.setdefault(lang.get("menu_bar.file.menu_name"), {}).setdefault(
            "exit", {}
        ).setdefault(
            f"{ensure_mnemonic(lang.get('menu_bar.file.close_world').replace('&', ''), 'c')}/{lang.get('menu_bar.file.quit').replace('&', '')}\tCtrl+Q",
            lambda evt: app.close_level(self.path),
        )
        return self.GetPage(self.GetSelection()).menu(menu)

    def _save_as(self):
        """Save the current world to a new location."""
        world = self.world
        current_path = world.level_path
        is_mcworld = current_path.lower().endswith('.mcworld')
        level_wrapper = world.level_wrapper
        current_world_name = level_wrapper.level_name
        is_bedrock = level_wrapper.platform == "bedrock"

        # Step 1: Custom dialog with world name + format radio buttons
        dialog = wx.Dialog(self, title="Save As", style=wx.DEFAULT_DIALOG_STYLE)
        sizer = wx.BoxSizer(wx.VERTICAL)

        sizer.Add(
            wx.StaticText(dialog, label="World name:"),
            0, wx.LEFT | wx.RIGHT | wx.TOP, 10,
        )
        name_ctrl = wx.TextCtrl(dialog, value=current_world_name)
        sizer.Add(name_ctrl, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        sizer.Add(
            wx.StaticText(dialog, label="Save format:"),
            0, wx.LEFT | wx.RIGHT | wx.TOP, 10,
        )
        rb_mcworld = wx.RadioButton(
            dialog, label=".mcworld file", style=wx.RB_GROUP,
        )
        rb_folder = wx.RadioButton(dialog, label="World directory")
        sizer.Add(rb_mcworld, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
        sizer.Add(rb_folder, 0, wx.LEFT | wx.RIGHT, 10)

        if is_mcworld:
            rb_mcworld.SetValue(True)
        else:
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

        new_world_name = name_ctrl.GetValue().strip()
        save_as_mcworld = rb_mcworld.GetValue()
        dialog.Destroy()

        if not new_world_name:
            SelectableMessageBox("Name cannot be empty.", "Error", wx.OK | wx.ICON_ERROR)
            return

        # Step 2: Pick the destination location
        default_parent = os.path.dirname(current_path)

        if save_as_mcworld:
            file_name = new_world_name
            if not file_name.lower().endswith('.mcworld'):
                file_name += '.mcworld'
            with wx.DirDialog(
                self,
                f"Choose where to save '{file_name}'",
                defaultPath=default_parent,
                style=wx.DD_DEFAULT_STYLE,
            ) as loc_dialog:
                if loc_dialog.ShowModal() == wx.ID_CANCEL:
                    return
                new_path = os.path.join(loc_dialog.GetPath(), file_name)
        else:
            if is_bedrock:
                folder_name = base64.b64encode(os.urandom(8)).decode("ascii")
            else:
                folder_name = new_world_name
            with wx.DirDialog(
                self,
                f"Choose where to save folder '{folder_name}'",
                defaultPath=default_parent,
                style=wx.DD_DEFAULT_STYLE,
            ) as loc_dialog:
                if loc_dialog.ShowModal() == wx.ID_CANCEL:
                    return
                new_path = os.path.join(loc_dialog.GetPath(), folder_name)

        if os.path.exists(new_path):
            if SelectableMessageBox(
                f"'{new_path}' already exists. Overwrite?",
                "Confirm Overwrite",
                wx.YES_NO | wx.ICON_QUESTION,
            ) != wx.YES:
                return

        src_platform = level_wrapper.platform
        src_version = level_wrapper.version
        overwrite = os.path.exists(new_path)

        if save_as_mcworld:
            from amulet.level.formats.leveldb_world import LevelDBFormat
            FormatClass = LevelDBFormat
        else:
            FormatClass = type(level_wrapper)

        # Run save in a thread with progress dialog
        progress_dialog = wx.ProgressDialog(
            "Save As",
            "Saving world to new location...",
            maximum=10000,
            parent=self,
            style=wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME | wx.PD_AUTO_HIDE,
        )
        progress_dialog.Fit()

        error_message = [None]

        def do_save():
            dest_world = None
            tmp_dir = None
            try:
                if save_as_mcworld:
                    tmp_dir = tempfile.mkdtemp(prefix="amulet_saveas_")
                    save_path = tmp_dir
                else:
                    save_path = new_path

                wx.CallAfter(progress_dialog.Update, 0, "Creating destination world...")
                dest_world = FormatClass(save_path)
                dest_world.create_and_open(
                    src_platform, src_version,
                    overwrite=True if save_as_mcworld else overwrite,
                )
                dest_world.level_name = new_world_name

                wx.CallAfter(progress_dialog.Update, 500, "Copying world data...")

                def progress_callback(chunk_index, chunk_total):
                    if chunk_total > 0:
                        pct = 500 + int((chunk_index / chunk_total) * 8500)
                        wx.CallAfter(progress_dialog.Update, min(pct, 9000))

                world.save(dest_world, progress_callback)

                wx.CallAfter(progress_dialog.Update, 9000, "Finalizing...")
                dest_world.close()
                dest_world = None

                if save_as_mcworld:
                    wx.CallAfter(progress_dialog.Update, 9200, "Packaging .mcworld file...")
                    if os.path.exists(new_path):
                        os.remove(new_path)
                    with zipfile.ZipFile(new_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                        for root, dirs, files in os.walk(tmp_dir):
                            for f in files:
                                abs_path = os.path.join(root, f)
                                arc_name = os.path.relpath(abs_path, tmp_dir)
                                zf.write(abs_path, arc_name)

            except Exception as e:
                if dest_world is not None:
                    try:
                        dest_world.close()
                    except Exception:
                        pass
                error_message[0] = str(e)
            finally:
                if tmp_dir is not None:
                    shutil.rmtree(tmp_dir, ignore_errors=True)

        save_thread = threading.Thread(target=do_save)
        save_thread.start()
        while save_thread.is_alive():
            save_thread.join(0.1)
            wx.Yield()
        progress_dialog.Update(10000)
        progress_dialog.Destroy()

        if error_message[0]:
            SelectableMessageBox(
                f"Failed to save world:\n{error_message[0]}",
                "Save As Error",
                wx.OK | wx.ICON_ERROR,
            )

    def _load_extensions(self):
        """Load and create instances of each of the extensions"""
        load_extensions()
        select = True
        for extension_name, extension in _extensions:
            try:
                ext = extension(self, self.world)
                self.AddPage(ext, extension_name, select)
                self._base_tab_labels[self.GetPageCount() - 1] = extension_name
                select = False
            except Exception as e:
                log.exception(
                    f"Failed to load extension {extension_name}\n{e}\n{traceback.format_exc()}"
                )
                continue

    def can_close(self) -> bool:
        """Check if all extensions are safe to be closed"""
        return all(
            self.GetPage(page).can_close() for page in range(self.GetPageCount())
        )

    def close(self):
        """
        Close the world and destroy the UI
        Check can_close before running this
        """
        for page in range(self.GetPageCount()):
            self.GetPage(page).close()

        # close the world in a new thread
        thread = threading.Thread(target=self.world.close)
        thread.start()
        # sleep a little
        thread.join(0.1)
        if thread.is_alive():
            # if not closed yet open a dialog to warn the user.
            # We do this on a delay so that it does not flick up for a split second
            dialog = wx.ProgressDialog(
                "Closing World",
                "Please be patient. This may take a little while.",
                maximum=100,
                style=wx.PD_APP_MODAL | wx.PD_ELAPSED_TIME | wx.PD_AUTO_HIDE,
            )
            dialog.Fit()
            dialog.Update(99)
            # wait until the world is closed then close the dialog
            while thread.is_alive():
                wx.GetApp().Yield()
                thread.join(0.1)
            dialog.Destroy()

    def _page_changing(self, evt: wx.BookCtrlEvent):
        """Method to fire when the page is changing."""
        if (
            self.GetSelection() != wx.NOT_FOUND
            and not self.GetPage(self.GetSelection()).can_disable()
        ):
            evt.Veto()

    def _page_changed(self, evt: wx.BookCtrlEvent):
        """Method to fire when the page has changed."""
        self._disable_page(evt.GetOldSelection())
        self._enable_page(evt.GetSelection())
        self._refresh_tab_highlight()
        # Force the tab strip to repaint immediately to show selection changes
        wx.CallAfter(self.Refresh)
        wx.CallAfter(self.SendSizeEvent)

    def _disable_page(self, page: Optional[int] = None):
        """Disable a page. Defaults to the current page."""
        page = self.GetSelection() if page is None else page
        if page != wx.NOT_FOUND:
            try:
                self.GetPage(page).disable()
            except Exception as e:
                log.critical(traceback.format_exc())
                # raise e

    def _enable_page(self, page: Optional[int] = None):
        """Enable a page. Defaults to the current page."""
        page = self.GetSelection() if page is None else page
        if page != wx.NOT_FOUND:
            try:
                self.GetPage(page).enable()
                self.GetTopLevelParent().create_menu()
            except Exception as e:
                log.critical(traceback.format_exc())
                dialog = TracebackDialog(
                    self,
                    "Exception loading sub-program",
                    str(e),
                    traceback.format_exc(),
                )
                dialog.ShowModal()
                dialog.Destroy()
                self.DeletePage(page)

    def can_disable(self) -> bool:
        return (
            self.GetSelection() == wx.NOT_FOUND
            or self.GetPage(self.GetSelection()).can_disable()
        )

    def disable(self):
        """Disable all containers in the world page"""
        self._disable_page()

    def enable(self):
        """Enable the world page"""
        self._enable_page()
        # On Windows, wx.Notebook with wx.NB_LEFT does not repaint the tab
        # strip until the user hovers over it.  Posting a size event after the
        # page is shown forces the tab area to redraw immediately.
        wx.CallAfter(self.SendSizeEvent)
