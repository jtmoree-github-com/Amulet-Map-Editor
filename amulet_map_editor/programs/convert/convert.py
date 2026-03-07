import wx
from threading import Thread
import webbrowser
import logging
import os
import base64
from typing import TYPE_CHECKING, Optional

from amulet import load_format
from amulet.api.level import BaseLevel
from amulet.api.errors import FormatError
from amulet.level.formats.anvil_world import AnvilFormat
from amulet.level.formats.leveldb_world import LevelDBFormat

from amulet_map_editor import lang
from amulet_map_editor.api.wx.ui.simple import SimplePanel, SimpleScrollablePanel
from amulet_map_editor.api.wx.ui.select_world import (
    minecraft_world_paths,
    get_world_image,
)
from amulet_map_editor.api.datatypes import MenuData
from amulet_map_editor.api.framework.menu_utils import ensure_mnemonic
from amulet_map_editor.api.framework.programs import BaseProgram

if TYPE_CHECKING:
    from amulet.api.wrapper import WorldFormatWrapper

log = logging.getLogger(__name__)


class ConvertExtension(SimpleScrollablePanel, BaseProgram):
    def __init__(self, container, world: BaseLevel):
        super().__init__(container)
        self._thread: Optional[Thread] = None
        self.world = world
        self.out_world_path: Optional[str] = None
        self._existing_world_paths: list[str] = []
        self._custom_new_world_root: Optional[str] = None
        self._new_world_folder_name: Optional[str] = None
        self._current_world_path_norm = os.path.normcase(
            os.path.normpath(self.world.level_path)
        )
        self._source_platform = self.world.level_wrapper.platform
        self._target_platform = "bedrock" if self._source_platform == "java" else "java"

        # Add title
        self._title = wx.StaticText(self, label=self._dynamic_title_text())
        font = self._title.GetFont()
        font.PointSize += 2
        font = font.Bold()
        self._title.SetFont(font)
        self.add_object(self._title, 0, wx.ALL | wx.CENTER)

        self._path_warning = wx.StaticText(self, wx.ID_ANY, "")
        self._path_warning.SetForegroundColour(wx.Colour(180, 30, 30))
        self._path_warning.Hide()
        self.add_object(self._path_warning, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM | wx.CENTER)

        # Output mode controls in the middle section
        self._mode_container = SimplePanel(self, wx.VERTICAL)
        self.add_object(self._mode_container, 0, wx.ALL | wx.CENTER)

        self._new_row = SimplePanel(self._mode_container, wx.HORIZONTAL)
        self._mode_container.add_object(self._new_row, 0, wx.ALL | wx.CENTER)
        self._new_world_radio = wx.RadioButton(
            self._new_row, wx.ID_ANY, "New World", style=wx.RB_GROUP
        )
        self._new_world_radio.SetValue(True)
        self._new_world_radio.Bind(wx.EVT_RADIOBUTTON, self._on_new_world_radio)
        self._new_row.add_object(self._new_world_radio, 0, wx.ALL | wx.CENTER)

        self._new_world_name = wx.TextCtrl(self._new_row, wx.ID_ANY, "")
        self._new_world_name.SetHint("New world name")
        self._new_world_name.Bind(wx.EVT_TEXT, self._on_new_world_name_changed)
        self._new_row.add_object(self._new_world_name, 0, wx.ALL | wx.CENTER)

        self._existing_row = SimplePanel(self._mode_container, wx.HORIZONTAL)
        self._mode_container.add_object(self._existing_row, 0, wx.ALL | wx.CENTER)
        self._existing_world_radio = wx.RadioButton(
            self._existing_row, wx.ID_ANY, "Existing World"
        )
        self._existing_world_radio.SetValue(False)
        self._existing_world_radio.Bind(wx.EVT_RADIOBUTTON, self._on_existing_world_radio)
        self._existing_row.add_object(self._existing_world_radio, 0, wx.ALL | wx.CENTER)

        self._existing_world_choice = wx.Choice(self._existing_row, wx.ID_ANY)
        self._existing_world_choice.Bind(wx.EVT_CHOICE, self._on_existing_world_selected)
        self._existing_row.add_object(self._existing_world_choice, 0, wx.ALL | wx.CENTER)

        # Prefill new world name/path so the UI is ready immediately.
        default_world_name = self.world.level_wrapper.level_name or "Converted World"
        self._new_world_name.SetValue(default_world_name)

        self._ensure_target_root_exists()

        self._populate_existing_worlds()

        # World previews under mode controls: Input -> Output
        self._world_preview_row = SimplePanel(self, wx.HORIZONTAL)
        self.add_object(self._world_preview_row, 0, wx.ALL | wx.CENTER)

        self._input = SimplePanel(self._world_preview_row, wx.VERTICAL)
        self._input_preview_slot = SimplePanel(self._input, wx.VERTICAL)
        self._input.add_object(self._input_preview_slot, 0, wx.ALL | wx.EXPAND)
        self._set_world_preview_card(self._input_preview_slot, self.world.level_wrapper)
        self._world_preview_row.add_object(self._input, 0, wx.ALL | wx.CENTER)

        self._direction_arrow = wx.StaticText(self._world_preview_row, wx.ID_ANY, "->")
        arrow_font = self._direction_arrow.GetFont()
        arrow_font.PointSize += 4
        arrow_font = arrow_font.Bold()
        self._direction_arrow.SetFont(arrow_font)
        self._world_preview_row.add_object(self._direction_arrow, 0, wx.ALL | wx.CENTER)

        self._output = SimplePanel(self._world_preview_row, wx.VERTICAL)
        self._output_preview_slot = SimplePanel(self._output, wx.VERTICAL)
        self._output.add_object(self._output_preview_slot, 0, wx.ALL | wx.CENTER)
        self._world_preview_row.add_object(self._output, 0, wx.ALL | wx.CENTER)

        # Progress bar on its own line, full width, hidden until conversion runs.
        self.loading_bar = wx.Gauge(
            self,
            wx.ID_ANY,
            100,
            wx.DefaultPosition,
            wx.DefaultSize,
            wx.GA_HORIZONTAL,
        )
        self.add_object(self.loading_bar, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP)
        self.loading_bar.SetValue(0)
        self.loading_bar.Hide()

        self._convert_bar = SimplePanel(self, wx.HORIZONTAL)
        self.add_object(self._convert_bar, 0, wx.ALL | wx.CENTER)

        self.convert_button = wx.Button(
            self._convert_bar,
            wx.ID_ANY,
            label=lang.get("program_convert.convert_button"),
        )
        self._convert_bar.add_object(self.convert_button)
        self.convert_button.Bind(wx.EVT_BUTTON, self._convert_event)

        if self._existing_world_paths:
            self._existing_world_choice.SetSelection(0)
        self._on_output_mode_change(None)

        # This panel is added to the notebook after __init__, so defer tab text update.
        wx.CallAfter(self._update_parent_tab_label)

    def menu(self, menu: MenuData) -> MenuData:
        try:
            menu.setdefault(lang.get("menu_bar.help.menu_name"), {}).setdefault(
                "control", {}
            ).setdefault(
                ensure_mnemonic(
                    lang.get("program_convert.menu_bar.help.user_guide"), "u"
                ),
                lambda evt: self._help_controls(),
            )
        except Exception:
            # Keep the Convert tab usable even if menu localization/setup fails.
            log.exception("Failed to build Convert menu")
        return menu

    def _target_platform_label(self) -> str:
        """Get a short display label for the target platform."""
        return self._platform_display_label(self._target_platform)

    def _source_platform_label(self) -> str:
        """Get a short display label for the source platform."""
        return self._platform_display_label(self._source_platform)

    def _conversion_title_text(self) -> str:
        """Build explicit conversion text: Convert <Source> World to <Target>."""
        return (
            f"{lang.get('program_convert.title')} "
            f"{self._source_platform_label()} World to {self._target_platform_label()}"
        )

    def _dynamic_title_text(self) -> str:
        """Build the page title shown inside the Convert tab."""
        return self._conversion_title_text()

    def _update_parent_tab_label(self):
        """Update the notebook tab label for this page to explicit conversion text."""
        parent = self.GetParent()
        if not isinstance(parent, wx.Notebook):
            return

        tab_text = self._conversion_title_text()
        for index in range(parent.GetPageCount()):
            if parent.GetPage(index) is self:
                parent.SetPageText(index, tab_text)
                break

    def _platform_display_label(self, platform_name: str) -> str:
        """Get a short, user-facing platform label for preview cards."""
        if platform_name == "java":
            return lang.get("world.java_platform")

        # Use the first token to avoid verbose variants like "Bedrock UWP".
        bedrock_label = lang.get("world.bedrock_uwp")
        if isinstance(bedrock_label, str) and bedrock_label:
            return bedrock_label.split()[0]
        return "Bedrock"

        if platform_name == "bedrock":
            bedrock_label = lang.get("world.bedrock_uwp")
            if isinstance(bedrock_label, str) and bedrock_label:
                return bedrock_label.split()[0]
            return "Bedrock"
        return platform_name.title()

    def _set_world_preview_card(self, slot: SimplePanel, world_format: "WorldFormatWrapper"):
        """Render a vertical preview card: image on top, details below."""
        for child in list(slot.GetChildren()):
            child.Destroy()

        img, width = get_world_image(world_format.world_image_path)
        slot.add_object(
            wx.StaticBitmap(slot, wx.ID_ANY, img, wx.DefaultPosition, (width, 128)),
            0,
            wx.ALL | wx.CENTER,
        )

        slot.add_object(
            wx.StaticText(
                slot,
                wx.ID_ANY,
                f"{world_format.level_name} ({self._platform_display_label(world_format.platform)})",
            ),
            0,
            wx.ALL | wx.CENTER,
        )

        path_text = wx.TextCtrl(
            slot,
            wx.ID_ANY,
            world_format.path,
            wx.DefaultPosition,
            wx.Size(520, -1),
            wx.TE_READONLY,
        )
        slot.add_object(path_text, 0, wx.ALL | wx.EXPAND)

        slot.Layout()
        slot.Fit()
        self.Layout()

    def _new_world_folder(self) -> str:
        """Get or create a stable world folder id in Minecraft-like Base64 form."""
        if not self._new_world_folder_name:
            # Use URL-safe base64 with padding to mirror common Bedrock world IDs.
            # 4 random bytes -> 8 chars, typically ending with "==".
            self._new_world_folder_name = base64.urlsafe_b64encode(
                os.urandom(4)
            ).decode("ascii")
        return self._new_world_folder_name

    def _reset_new_world_folder(self):
        self._new_world_folder_name = None

    def _set_new_world_preview(self, path_text: str):
        """Render New World output preview with selectable path and browse button."""
        for child in list(self._output_preview_slot.GetChildren()):
            child.Destroy()

        preview_text = wx.TextCtrl(
            self._output_preview_slot,
            wx.ID_ANY,
            path_text,
            wx.DefaultPosition,
            wx.Size(520, -1),
            wx.TE_READONLY,
        )
        self._output_preview_slot.add_object(preview_text, 0, wx.ALL | wx.EXPAND)

        browse_button = wx.Button(self._output_preview_slot, wx.ID_ANY, "Browse...")
        browse_button.Bind(wx.EVT_BUTTON, self._on_new_world_browse)
        self._output_preview_slot.add_object(browse_button, 0, wx.ALL | wx.CENTER)

        self._output_preview_slot.Layout()
        self._output_preview_slot.Fit()
        self._output.Layout()
        self._output.Fit()
        self.Layout()

    def _on_new_world_browse(self, _evt):
        """Select a custom parent folder for new-world output."""
        start_dir = self._custom_new_world_root or self._target_root_dir() or os.path.expanduser("~")
        dlg = wx.DirDialog(
            self,
            "Choose output folder",
            defaultPath=start_dir,
            style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST,
        )
        try:
            if dlg.ShowModal() != wx.ID_OK:
                return
            self._custom_new_world_root = dlg.GetPath()
        finally:
            dlg.Destroy()

        self._reset_new_world_folder()
        self._on_output_mode_change(None)

    def enable(self):
        """Called when the Convert tab becomes active."""
        # Keep this hook exception-safe so tab switches never drop this page.
        return

    def disable(self):
        """Called when the Convert tab becomes inactive."""
        return

    def _help_controls(self):
        webbrowser.open(
            "https://github.com/Amulet-Team/Amulet-Map-Editor/blob/master/amulet_map_editor/programs/convert/readme.md"
        )

    def _populate_existing_worlds(self):
        """Populate existing-world dropdown with opposite-platform worlds only."""
        labels: list[str] = []
        paths: list[str] = []

        for group_name, directory in minecraft_world_paths:
            if not os.path.isdir(directory):
                continue
            try:
                for child in sorted(os.listdir(directory)):
                    world_path = os.path.join(directory, child)
                    if not os.path.isdir(world_path):
                        continue
                    try:
                        world_format = load_format(world_path)
                    except (FormatError, Exception):
                        continue

                    # Avoid converting to the currently open world.
                    world_path_norm = os.path.normcase(os.path.normpath(world_format.path))
                    if world_path_norm == self._current_world_path_norm:
                        continue

                    # Only show opposite-format targets.
                    if world_format.platform != self._target_platform:
                        continue

                    labels.append(f"{world_format.level_name} ({group_name})")
                    paths.append(world_format.path)
            except Exception:
                continue

        self._existing_world_paths = paths
        self._existing_world_choice.SetItems(labels)

    def _target_root_dir(self) -> Optional[str]:
        """Return the expected root directory for the target platform."""
        token = "minecraftworlds" if self._target_platform == "bedrock" else "saves"

        # Prefer the folder that already contains detected target worlds.
        if self._existing_world_paths:
            parent_counts: dict[str, int] = {}
            for world_path in self._existing_world_paths:
                parent = os.path.dirname(world_path)
                parent_counts[parent] = parent_counts.get(parent, 0) + 1

            if parent_counts:
                if self._target_platform == "bedrock":
                    def _score(item):
                        parent, count = item
                        parent_norm = os.path.normcase(parent)
                        roaming_pref = 1 if "\\roaming\\" in parent_norm else 0
                        return (count, roaming_pref)

                    return max(parent_counts.items(), key=_score)[0]

                return max(parent_counts.items(), key=lambda item: item[1])[0]

        # Fall back to platform-standard paths from the known list.
        for _, directory in minecraft_world_paths:
            if token in directory.lower():
                return directory
        return None

    def _ensure_target_root_exists(self):
        """Create expected target root directory if missing; warn on failure."""
        target_root = self._target_root_dir()
        if not target_root:
            return

        if os.path.isdir(target_root):
            self._path_warning.Hide()
            return

        try:
            os.makedirs(target_root, exist_ok=True)
            self._path_warning.Hide()
        except Exception as e:
            self._path_warning.SetLabel(
                f"Warning: could not create expected {self._target_platform.title()} world folder. "
                "File operations may fail."
            )
            self._path_warning.SetToolTip(f"Path: {target_root}\nError: {e}")
            self._path_warning.Show()
            self.Layout()

    def _refresh_existing_worlds(self, select_path: Optional[str] = None):
        """Refresh existing-world list and optionally select a specific path."""
        self._populate_existing_worlds()

        if select_path is not None:
            try:
                index = self._existing_world_paths.index(select_path)
            except ValueError:
                pass
            else:
                self._existing_world_choice.SetSelection(index)
                return

        if self._existing_world_paths and self._existing_world_choice.GetSelection() == wx.NOT_FOUND:
            self._existing_world_choice.SetSelection(0)

    def _on_new_world_radio(self, _evt):
        """Keep radio buttons mutually exclusive across separate row panels."""
        self._new_world_radio.SetValue(True)
        self._existing_world_radio.SetValue(False)
        self._on_output_mode_change(None)

    def _on_existing_world_radio(self, _evt):
        """Keep radio buttons mutually exclusive across separate row panels."""
        self._existing_world_radio.SetValue(True)
        self._new_world_radio.SetValue(False)
        self._on_output_mode_change(None)

    def _on_output_mode_change(self, _evt):
        # Radios live in different row panels; treat Existing as active only
        # when explicitly selected and New is not selected.
        existing_mode = self._existing_world_radio.GetValue() and not self._new_world_radio.GetValue()
        self._existing_world_choice.Enable(existing_mode)
        self._new_world_name.Enable(not existing_mode)

        if existing_mode:
            if self._existing_world_choice.GetSelection() != wx.NOT_FOUND:
                index = self._existing_world_choice.GetSelection()
                if 0 <= index < len(self._existing_world_paths):
                    self._select_existing_output_world(self._existing_world_paths[index])
                    return

            self.out_world_path = None
            self._set_output_preview_text(
                f"No existing {self._target_platform.title()} worlds found"
            )
        else:
            self.out_world_path = None
            world_name = self._new_world_name.GetValue().strip()
            if world_name:
                preview_path = self._default_new_world_path(world_name)
                self._set_new_world_preview(preview_path)
            else:
                self._set_new_world_preview("(not set)")

    def _on_existing_world_selected(self, _evt):
        index = self._existing_world_choice.GetSelection()
        if 0 <= index < len(self._existing_world_paths):
            self._select_existing_output_world(self._existing_world_paths[index])

    def _on_new_world_name_changed(self, _evt):
        if not self._new_world_radio.GetValue():
            return
        world_name = self._new_world_name.GetValue().strip()
        if world_name:
            preview_path = self._default_new_world_path(world_name)
            self._set_new_world_preview(preview_path)
        else:
            self._set_new_world_preview("(not set)")

    def _select_existing_output_world(self, path: str):
        if path == self.world.level_path:
            wx.MessageBox(lang.get("program_convert.input_output_must_different"))
            return
        try:
            out_world_format = load_format(path)
            self.out_world_path = path
        except Exception:
            return

        self._set_world_preview_card(self._output_preview_slot, out_world_format)

    def _set_output_preview_text(self, text: str):
        for child in list(self._output_preview_slot.GetChildren()):
            child.Destroy()
        preview_text = wx.TextCtrl(
            self._output_preview_slot,
            wx.ID_ANY,
            text,
            wx.DefaultPosition,
            wx.Size(520, -1),
            wx.TE_READONLY,
        )
        self._output_preview_slot.add_object(
            preview_text, 0, wx.ALL | wx.EXPAND
        )
        self._output_preview_slot.Layout()
        self._output_preview_slot.Fit()
        self._output.Layout()
        self._output.Fit()
        self.Layout()

    def _default_new_world_path(self, world_name: str) -> str:
        """Choose a default output path for a new world based on target platform."""
        target_root = self._custom_new_world_root or self._target_root_dir()
        if target_root and os.path.isdir(target_root):
            return os.path.join(target_root, self._new_world_folder())

        return os.path.join(os.path.expanduser("~"), self._new_world_folder())

    def _create_new_output_world(self, world_name: str) -> str:
        """Create a new blank world in the opposite format and return its path."""
        output_path = self._default_new_world_path(world_name)
        overwrite = False
        if os.path.exists(output_path):
            dlg = wx.MessageDialog(
                self,
                (
                    f"A world already exists at:\n{output_path}\n\n"
                    "Do you want to overwrite it?"
                ),
                "Overwrite Existing World?",
                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_WARNING,
            )
            try:
                if dlg.ShowModal() != wx.ID_YES:
                    raise RuntimeError("Conversion cancelled by user")
                overwrite = True
            finally:
                dlg.Destroy()

        wrapper_cls = LevelDBFormat if self._target_platform == "bedrock" else AnvilFormat
        out_world = wrapper_cls(output_path)
        platform, version = out_world.max_world_version
        out_world.create_and_open(platform, version, overwrite=overwrite)
        try:
            out_world.level_name = world_name
            out_world.save()
        finally:
            out_world.close()

        return output_path

    def _update_loading_bar(self, chunk_index, chunk_total):
        wx.CallAfter(self.loading_bar.SetValue, int(100 * chunk_index / chunk_total))

    def _set_loading_bar_visible(self, visible: bool):
        if visible:
            self.loading_bar.SetValue(0)
            self.loading_bar.Show()
        else:
            self.loading_bar.Hide()
            self.loading_bar.SetValue(0)
        self.Layout()

    def _convert_event(self, evt):
        if self._existing_world_radio.GetValue():
            if self.out_world_path is None:
                wx.MessageBox(lang.get("program_convert.select_before_converting"))
                return
        else:
            world_name = self._new_world_name.GetValue().strip()
            if not world_name:
                wx.MessageBox("Please enter a new world name.")
                return
            try:
                self.out_world_path = self._create_new_output_world(world_name)
                self._refresh_existing_worlds(self.out_world_path)
                self._set_new_world_preview(self.out_world_path)
            except Exception as e:
                if str(e) == "Conversion cancelled by user":
                    return
                wx.MessageBox(f"Could not create new world.\n{e}")
                return

        self.convert_button.Disable()
        self._set_loading_bar_visible(True)
        self._thread = Thread(target=self._convert_method)
        self._thread.start()

    def _convert_method(self):
        try:
            out_world = load_format(self.out_world_path)
            log.info(f"Converting world {self.world.level_path} to {out_world.path}")
            out_world: WorldFormatWrapper
            out_world.open()
            self.world.save(out_world, self._update_loading_bar)
            out_world.close()
            message = lang.get("program_convert.conversion_completed")
            log.info(
                f"Finished converting world {self.world.level_path} to {out_world.path}"
            )
        except Exception as e:
            message = f"Error during conversion\n{e}"
            log.error(message, exc_info=True)
        self._update_loading_bar(0, 100)
        wx.CallAfter(self._set_loading_bar_visible, False)
        wx.CallAfter(self._refresh_existing_worlds, self.out_world_path)
        self._thread = None
        self.convert_button.Enable()
        wx.MessageBox(message)

    def can_close(self):
        if self._thread is not None:
            log.info(
                f"World {self.world.level_path} is still being converted. Please let it finish before closing"
            )
            return False
        return True
