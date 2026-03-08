from typing import TYPE_CHECKING, Optional
from math import floor, log10
import wx

from amulet_map_editor.programs.edit.api.edit_canvas_container import (
    EditCanvasContainer,
)
from amulet_map_editor.api.wx.ui.simple import SimpleChoiceAny
from amulet_map_editor.programs.edit.api.events import (
    EVT_CAMERA_MOVED,
    EVT_SPEED_CHANGED,
    EVT_PROJECTION_CHANGED,
    EVT_DIMENSION_CHANGE,
    DimensionChangeEvent,
    EditCloseEvent,
    ToolChangeEvent,
)
from amulet_map_editor.api import image, lang
from amulet_map_editor.api.opengl.camera import Projection
from amulet_map_editor.api.wx.util.key_config import stringify_key, format_key_display
from amulet_map_editor.programs.edit.api.key_config import ACT_TOGGLE_WASD_MODE

if TYPE_CHECKING:
    from amulet_map_editor.programs.edit.api.canvas import EditCanvas


def _format_float(num: float) -> str:
    if num < 100:
        return f"{num:.0{max(0, 2 - floor(log10(num)))}f}".rstrip("0").rstrip(".")
    else:
        return f"{num:.0f}"


def _set_inverted_colors(button: wx.Button, is_active: bool) -> None:
    """Set inverted colors on a button based on its active state.
    
    Args:
        button: The button to style
        is_active: If True, use dark background with light text.
                   If False, use light background with dark text.
    """
    if not button:
        return
    
    if is_active:
        # Dark background with light/white text
        button.SetBackgroundColour(wx.Colour(0, 0, 0))  # Black background
        button.SetForegroundColour(wx.Colour(255, 255, 255))  # White text
    else:
        # Light background with dark text (system default)
        button.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE))
        button.SetForegroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNTEXT))
    
    button.Refresh()
    button.Update()



class FilePanel(EditCanvasContainer):
    def __init__(self, canvas: "EditCanvas"):
        super().__init__(canvas)

        level = self.canvas.world
        from amulet_map_editor.api import image

        # Toolbar panel (undo/redo/save) at top-left
        self._toolbar_panel = wx.Panel(canvas.GetParent())
        self._toolbar_panel.SetBackgroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
        )
        self._toolbar_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._toolbar_panel.SetSizer(self._toolbar_sizer)

        def add_toolbar_button(label: str, tooltip: str, callback, bitmap=None):
            button = wx.Button(self._toolbar_panel, label=label)
            if bitmap is not None:
                button.SetBitmap(bitmap)
            button.SetToolTip(tooltip)

            def on_button_down(evt):
                canvas.SetFocus()
                evt.Skip()

            def wrapped_callback(evt):
                canvas.SetFocus()
                callback(evt)
                wx.CallAfter(canvas.SetFocus)

            button.Bind(wx.EVT_LEFT_DOWN, on_button_down)
            button.Bind(wx.EVT_BUTTON, wrapped_callback)
            self._toolbar_sizer.Add(button, 0, wx.ALL, 2)
            return button

        add_toolbar_button(
            lang.get("program_3d_edit.menu_bar.edit.undo"),
            f"{lang.get('program_3d_edit.file_ui.undo_tooltip')} (Ctrl+Z)",
            lambda evt: canvas.undo(),
            image.icon.tablericons.arrow_back_up.bitmap(20, 20),
        )
        add_toolbar_button(
            lang.get("program_3d_edit.menu_bar.edit.redo"),
            f"{lang.get('program_3d_edit.file_ui.redo_tooltip')} (Ctrl+Y)",
            lambda evt: canvas.redo(),
            image.icon.tablericons.arrow_forward_up.bitmap(20, 20),
        )
        self._toolbar_sizer.AddSpacer(8)
        add_toolbar_button(
            lang.get("program_3d_edit.menu_bar.file.save"),
            f"{lang.get('program_3d_edit.file_ui.save_tooltip')} (Ctrl+S)",
            lambda evt: canvas.save(),
            image.icon.tablericons.device_floppy.bitmap(20, 20),
        )

        # Version panel at top-left below toolbar
        self._version_panel = wx.Panel(canvas.GetParent())
        self._version_panel.SetBackgroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
        )
        self._version_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._version_panel.SetSizer(self._version_sizer)
        self._version_text = wx.StaticText(
            self._version_panel,
            label=f"{level.level_wrapper.platform}, {level.level_wrapper.version}",
        )
        self._version_sizer.Add(self._version_text)
        self._version_text.SetToolTip(
            lang.get("program_3d_edit.file_ui.version_tooltip")
        )

        self._button_window = wx.Panel(canvas.GetParent())
        self._button_window.SetBackgroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
        )
        self._button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._button_window.SetSizer(self._button_sizer)

        self._projection_button = wx.Button(self._button_window, label="3D")
        self._projection_button.SetToolTip(
            lang.get("program_3d_edit.file_ui.projection_tooltip")
        )
        self._projection_button.Bind(wx.EVT_BUTTON, self._on_projection_button)
        # Initialize projection button color (3D is default, 2D is inverted)
        _set_inverted_colors(self._projection_button, self.canvas.camera.projection_mode == Projection.TOP_DOWN)
        self._button_sizer.Add(self._projection_button)
        
        self._move_button = wx.Button(self._button_window, label=lang.get("program_3d_edit.file_ui.move_camera_label"))
        self._move_button.SetToolTip(self._get_move_button_tooltip())
        self._move_button.Bind(wx.EVT_BUTTON, self._on_move_button)
        # Initialize move button color (camera mode is default, so light background)
        _set_inverted_colors(self._move_button, self.canvas.wasd_moves_cursor)
        self._button_sizer.Add(self._move_button)
        
        self._location_button = wx.Button(
            self._button_window,
            label=", ".join([f"{s:.2f}" for s in self.canvas.camera.location]),
        )
        self._location_button.SetToolTip(
            lang.get("program_3d_edit.file_ui.location_tooltip")
        )
        self._location_button.Bind(wx.EVT_BUTTON, lambda evt: self.canvas.goto())
        self._button_sizer.Add(self._location_button)

        def set_speed(evt):
            dialog = SpeedSelectDialog(
                canvas, self.canvas.camera.move_speed * 1000 / 33
            )
            if dialog.ShowModal() == wx.ID_OK:
                self.canvas.camera.move_speed = dialog.speed * 33 / 1000

        self._speed_button = wx.Button(
            self._button_window,
            label=f"{_format_float(self.canvas.camera.move_speed * 1000 / 33)} {lang.get('program_3d_edit.file_ui.speed_blocks_per_second')}",
        )
        self._speed_button.SetToolTip(lang.get("program_3d_edit.file_ui.speed_tooltip"))
        self._speed_button.Bind(wx.EVT_BUTTON, set_speed)
        self._button_sizer.Add(self._speed_button)

        self._dim_options = SimpleChoiceAny(self._button_window)
        self._dim_options.SetToolTip(lang.get("program_3d_edit.file_ui.dim_tooltip"))
        self._dim_options.SetItems(level.level_wrapper.dimensions)
        self._set_dimension(canvas.dimension)
        self._dim_options.Bind(wx.EVT_CHOICE, self._on_dimension_change)

        self._button_sizer.Add(self._dim_options)

        # Mode selection dropdown (F1-F10 tools)
        self._mode_choice = SimpleChoiceAny(self._button_window, sort=False)
        self._mode_choice.SetToolTip("Select editing mode (F1-F10)")
        self._mode_choice.Bind(wx.EVT_CHOICE, self._on_mode_choice)
        self._button_sizer.Add(self._mode_choice, 0, wx.ALIGN_CENTER_VERTICAL)

        self._button_sizer.AddSpacer(8)

        def create_button(text, operation):
            button = wx.Button(self._button_window, label=text)
            button.Bind(wx.EVT_BUTTON, operation)
            self._button_sizer.Add(button)
            return button

        self._close_button = create_button(
            "", lambda evt: wx.PostEvent(self.canvas, EditCloseEvent())
        )
        self._close_button.SetBitmap(image.icon.tablericons.square_x.bitmap(20, 20))
        self._close_button.SetToolTip(lang.get("program_3d_edit.file_ui.close_tooltip"))
        size = self._close_button.GetSize()
        self._close_button.SetSize(wx.Size(size.GetHeight(), size.GetHeight()))
        self._close_button.SetMinSize(wx.Size(size.GetHeight(), size.GetHeight()))

        self._resize()

    def bind_events(self):
        self.canvas.Bind(EVT_CAMERA_MOVED, self._on_camera_move)
        self.canvas.Bind(EVT_SPEED_CHANGED, self._on_speed_change)
        self.canvas.Bind(EVT_PROJECTION_CHANGED, self._on_projection_change)
        self.canvas.Bind(EVT_DIMENSION_CHANGE, self._change_dimension)
        self.canvas.Bind(wx.EVT_SIZE, self._on_resize)

    def _on_dimension_change(self, evt):
        """Run when the dimension selection is changed by the user."""
        dimension = self._dim_options.GetCurrentObject()
        if dimension is not None:
            self.canvas.dimension = dimension
        evt.Skip()

    def _on_mode_choice(self, evt):
        """Handle mode selection from the dropdown."""
        selection = self._mode_choice.GetCurrentObject()
        if selection:
            tool_name, state_name = selection
            state = None
            if state_name and state_name != "None":
                state = {"operation_name": state_name}
            wx.PostEvent(self.canvas, ToolChangeEvent(tool=tool_name, state=state))
        evt.Skip()

    def set_mode_choice_items(self, items):
        """Set the available items in the mode choice dropdown."""
        self._mode_choice.SetItems(items)

    def update_mode_choice_selection(self, tool_name: str, state_name):
        """Update the dropdown to reflect the current tool/state."""
        target_tuple = (tool_name, state_name)
        if target_tuple in self._mode_choice.values:
            idx = self._mode_choice.values.index(target_tuple)
            self._mode_choice.SetSelection(idx)

    def _on_projection_change(self, evt):
        if self.canvas.camera.projection_mode == Projection.PERSPECTIVE:
            self._projection_button.SetLabel("3D")
            _set_inverted_colors(self._projection_button, False)
        elif self.canvas.camera.projection_mode == Projection.TOP_DOWN:
            self._projection_button.SetLabel("2D")
            _set_inverted_colors(self._projection_button, True)
        evt.Skip()

    def _on_projection_button(self, evt):
        if self.canvas.camera.projection_mode == Projection.PERSPECTIVE:
            self.canvas.camera.projection_mode = Projection.TOP_DOWN
        else:
            self.canvas.camera.projection_mode = Projection.PERSPECTIVE
        evt.Skip()

    def _on_move_button(self, evt):
        self.canvas.wasd_moves_cursor = not self.canvas.wasd_moves_cursor
        evt.Skip()

    def update_move_button(self):
        """Update the move button label based on the current state."""
        if self.canvas.wasd_moves_cursor:
            self._move_button.SetLabel(lang.get("program_3d_edit.file_ui.move_cursor_label"))
            _set_inverted_colors(self._move_button, True)
        else:
            self._move_button.SetLabel(lang.get("program_3d_edit.file_ui.move_camera_label"))
            _set_inverted_colors(self._move_button, False)
        self._move_button.SetToolTip(self._get_move_button_tooltip())

    def _get_move_button_tooltip(self) -> str:
        tooltip = lang.get("program_3d_edit.file_ui.move_button_tooltip")
        keybind = self.canvas.key_binds.get(ACT_TOGGLE_WASD_MODE)
        if keybind:
            # key_binds may return a list of bindings per action
            if isinstance(keybind, list):
                for b in keybind:
                    mod, trig = b
                    if not (isinstance(trig, str) and trig.startswith("CONTROLLER_")):
                        keybind = b
                        break
                else:
                    keybind = keybind[0] if keybind else None
            if keybind:
                hotkey_text = format_key_display(stringify_key(keybind))
                return f"{tooltip} Hotkey: {hotkey_text}"
        return tooltip

    def _change_dimension(self, evt: DimensionChangeEvent):
        """Run when the dimension attribute in the canvas is changed.
        This is run when the user changes the attribute and when it is changed manually in code.
        """
        self._set_dimension(evt.dimension)

    def _set_dimension(self, dimension: str) -> None:
        index = self._dim_options.FindString(dimension)
        if not (index == wx.NOT_FOUND or index == self._dim_options.GetSelection()):
            self._dim_options.SetSelection(index)

    def _on_camera_move(self, evt):
        x, y, z = evt.camera_location
        label = f"{x:.2f}, {y:.2f}, {z:.2f}"
        old_label = self._location_button.GetLabel()
        self._location_button.SetLabel(label)
        if len(label) != len(old_label):
            self._resize()
        evt.Skip()

    def _on_speed_change(self, evt):
        label = f"{_format_float(self.canvas.camera.move_speed * 1000 / 33)} {lang.get('program_3d_edit.file_ui.speed_blocks_per_second')}"
        old_label = self._speed_button.GetLabel()
        self._speed_button.SetLabel(label)
        if len(label) != len(old_label):
            self._resize()
        evt.Skip()

    def _on_resize(self, evt) -> None:
        self._resize()
        evt.Skip()

    def _resize(self) -> None:
        # Position toolbar at top-left
        toolbar_size = self._toolbar_panel.GetBestSize()
        self._toolbar_panel.SetSize(
            wx.Rect(0, 0, toolbar_size.GetWidth(), toolbar_size.GetHeight())
        )
        self._toolbar_panel.Raise()

        # Position version panel below toolbar at top-left
        version_text_size = self._version_panel.GetBestSize()
        toolbar_height = toolbar_size.GetHeight()
        self._version_panel.SetSize(
            wx.Rect(
                0,
                toolbar_height + 2,
                version_text_size.GetWidth(),
                version_text_size.GetHeight(),
            )
        )
        self._version_panel.Raise()

        # Position button window at top-right
        self._button_window.Layout()
        window_size = self._button_window.GetBestSize()
        canvas_size = self.canvas.GetSize()
        self._button_window.SetSize(
            wx.Rect(
                max(0, canvas_size.GetWidth() - window_size.GetWidth()),
                0,
                window_size.GetWidth(),
                window_size.GetHeight(),
            )
        )
        self._button_window.Raise()
        self._button_window.Refresh(False)


class SpeedSelectDialog(wx.Dialog):
    def __init__(self, parent: wx.Window, speed: float):
        wx.Dialog.__init__(self, parent)
        self.SetTitle(lang.get("program_3d_edit.file_ui.speed_dialog_name"))

        sizer = wx.BoxSizer(wx.VERTICAL)

        self._speed_spin_ctrl_double = wx.SpinCtrlDouble(
            self, wx.ID_ANY, initial=speed, min=0.0, max=1_000_000_000.0
        )
        self._speed_spin_ctrl_double.SetToolTip(
            lang.get("program_3d_edit.file_ui.speed_tooltip")
        )

        def on_mouse_wheel(evt: wx.MouseEvent):
            if evt.GetWheelRotation() > 0:
                self._speed_spin_ctrl_double.SetValue(
                    self._speed_spin_ctrl_double.GetValue()
                    + self._speed_spin_ctrl_double.GetIncrement()
                )
            else:
                self._speed_spin_ctrl_double.SetValue(
                    self._speed_spin_ctrl_double.GetValue()
                    - self._speed_spin_ctrl_double.GetIncrement()
                )

        self._speed_spin_ctrl_double.Bind(wx.EVT_MOUSEWHEEL, on_mouse_wheel)
        self._speed_spin_ctrl_double.SetIncrement(1.0)
        self._speed_spin_ctrl_double.SetDigits(4)
        sizer.Add(self._speed_spin_ctrl_double)

        button_sizer = wx.StdDialogButtonSizer()
        sizer.Add(button_sizer, 0, wx.ALIGN_RIGHT | wx.ALL, 4)

        self._button_ok = wx.Button(self, wx.ID_OK, "")
        self._button_ok.SetDefault()
        button_sizer.AddButton(self._button_ok)

        self._button_cancel = wx.Button(self, wx.ID_CANCEL, "")
        button_sizer.AddButton(self._button_cancel)

        button_sizer.Realize()

        self.SetSizer(sizer)
        sizer.Fit(self)

        self.SetAffirmativeId(self._button_ok.GetId())
        self.SetEscapeId(self._button_cancel.GetId())

        self.Layout()

    @property
    def speed(self) -> float:
        return self._speed_spin_ctrl_double.GetValue()
