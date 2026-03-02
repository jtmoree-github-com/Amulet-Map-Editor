from typing import TYPE_CHECKING, Callable, Tuple
import logging
import math
import math

import wx
from OpenGL.GL import (
    glClear,
    GL_DEPTH_BUFFER_BIT,
)

from amulet.api.data_types import BlockCoordinates

from amulet_map_editor import lang
from amulet_map_editor.api.wx.ui.simple import SimpleScrollablePanel
from amulet_map_editor.api.wx.util.validators import IntValidator
from amulet_map_editor.api.opengl.camera import Projection, Camera
from amulet_map_editor.programs.edit.api.events import EVT_SELECTION_CHANGE
from amulet_map_editor.programs.edit.api.behaviour.inspect_block_behaviour import (
    InspectBlockBehaviour,
)
from amulet_map_editor.programs.edit.api.behaviour.block_selection_behaviour import (
    BlockSelectionBehaviour,
    EVT_RENDER_BOX_CHANGE,
    RenderBoxChangeEvent,
    EVT_RENDER_BOX_DISABLE_INPUTS,
    EVT_RENDER_BOX_ENABLE_INPUTS,
)
from amulet_map_editor.programs.edit.api.ui.tool import DefaultBaseToolUI
from amulet_map_editor.programs.edit.api.key_config import (
    ACT_CURSOR_UP,
    ACT_CURSOR_DOWN,
    ACT_CURSOR_FORWARDS,
    ACT_CURSOR_BACKWARDS,
    ACT_CURSOR_LEFT,
    ACT_CURSOR_RIGHT,
    ACT_LOOK_UP,
    ACT_LOOK_DOWN,
    ACT_LOOK_LEFT,
    ACT_LOOK_RIGHT,
    ACT_TOGGLE_MOVE_TARGET,
    ACT_TOGGLE_WASD_MODE,
    ACT_MOVE_UP,
    ACT_MOVE_DOWN,
    ACT_MOVE_FORWARDS,
    ACT_MOVE_BACKWARDS,
    ACT_MOVE_LEFT,
    ACT_MOVE_RIGHT,
)
from amulet_map_editor.programs.edit.api.events import (
    InputPressEvent,
    InputHeldEvent,
    EVT_INPUT_PRESS,
    EVT_INPUT_HELD,
)
from amulet_map_editor.api.opengl.matrix import rotation_matrix_xy
import numpy

if TYPE_CHECKING:
    from amulet_map_editor.programs.edit.api.canvas import EditCanvas


log = logging.getLogger(__name__)
paint_log_count = 0


class SelectTool(wx.BoxSizer, DefaultBaseToolUI):
    _x1: wx.SpinCtrl
    _y1: wx.SpinCtrl
    _z1: wx.SpinCtrl
    _x2: wx.SpinCtrl
    _y2: wx.SpinCtrl
    _z2: wx.SpinCtrl

    def __init__(self, canvas: "EditCanvas"):
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        DefaultBaseToolUI.__init__(self, canvas)

        self._selection = BlockSelectionBehaviour(self.canvas)
        self._inspect_block = InspectBlockBehaviour(self.canvas, self._selection)

        self._button_panel = SimpleScrollablePanel(canvas.Parent)
        self._button_panel.SetBackgroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
        )
        button_sizer = wx.BoxSizer(wx.VERTICAL)
        self._button_panel.SetSizer(button_sizer)

        def add_button(
            label: str, tooltip: str, action: Callable[[wx.PyEventBinder], None]
        ):
            button = wx.Button(self._button_panel, label=label)
            button.SetToolTip(tooltip)
            button_sizer.Add(button, 0, wx.ALL | wx.EXPAND, 5)
            def wrapped_action(evt):
                action(evt)
                wx.CallAfter(self.canvas.SetFocus)

            button.Bind(wx.EVT_BUTTON, wrapped_action)
            button.Bind(wx.EVT_ENTER_WINDOW, self._on_tool_ui_hover)

        add_button(
            lang.get("program_3d_edit.select_tool.delete_button"),
            lang.get("program_3d_edit.select_tool.delete_button_tooltip"),
            lambda evt: self.canvas.delete(),
        )
        add_button(
            lang.get("program_3d_edit.select_tool.copy_button"),
            lang.get("program_3d_edit.select_tool.copy_button_tooltip"),
            lambda evt: self.canvas.copy(),
        )
        add_button(
            lang.get("program_3d_edit.select_tool.cut_button"),
            lang.get("program_3d_edit.select_tool.cut_button_tooltip"),
            lambda evt: self.canvas.cut(),
        )
        add_button(
            lang.get("program_3d_edit.select_tool.paste_button"),
            lang.get("program_3d_edit.select_tool.paste_button_tooltip"),
            lambda evt: self.canvas.paste_from_cache(),
        )

        self._x1 = self._add_spin_ctrl(
            lang.get("program_3d_edit.select_tool.scroll_point_x1"),
            lang.get("program_3d_edit.select_tool.scroll_point_x1_tooltip"),
            (160, 215, 145),
        )
        self._y1 = self._add_spin_ctrl(
            lang.get("program_3d_edit.select_tool.scroll_point_y1"),
            lang.get("program_3d_edit.select_tool.scroll_point_y1_tooltip"),
            (160, 215, 145),
        )
        self._z1 = self._add_spin_ctrl(
            lang.get("program_3d_edit.select_tool.scroll_point_z1"),
            lang.get("program_3d_edit.select_tool.scroll_point_z1_tooltip"),
            (160, 215, 145),
        )
        self._x2 = self._add_spin_ctrl(
            lang.get("program_3d_edit.select_tool.scroll_point_x2"),
            lang.get("program_3d_edit.select_tool.scroll_point_x2_tooltip"),
            (150, 150, 215),
        )
        self._y2 = self._add_spin_ctrl(
            lang.get("program_3d_edit.select_tool.scroll_point_y2"),
            lang.get("program_3d_edit.select_tool.scroll_point_y2_tooltip"),
            (150, 150, 215),
        )
        self._z2 = self._add_spin_ctrl(
            lang.get("program_3d_edit.select_tool.scroll_point_z2"),
            lang.get("program_3d_edit.select_tool.scroll_point_z2_tooltip"),
            (150, 150, 215),
        )

        self._box_size_selector_fstring = lang.get(
            "program_3d_edit.select_tool.box_size_selector_fstring"
        )
        try:
            box_size_fstring = self._box_size_selector_fstring.format(x=0, y=0, z=0)
        except:
            self._box_size_selector_fstring = "dx={x},dy={y},dz={z}"
            box_size_fstring = self._box_size_selector_fstring.format(x=0, y=0, z=0)
        self._box_size_selector_text = wx.StaticText(
            self._button_panel, label=box_size_fstring, style=wx.ALIGN_CENTER_HORIZONTAL
        )
        self._box_size_selector_text.SetToolTip(
            lang.get("program_3d_edit.select_tool.box_size_selector_tooltip")
        )
        button_sizer.Add(self._box_size_selector_text, 0, wx.ALL | wx.EXPAND, 5)

        self._box_volume_text = wx.StaticText(
            self._button_panel, label="0x0x0=0", style=wx.ALIGN_CENTER_HORIZONTAL
        )
        button_sizer.Add(self._box_volume_text, 0, wx.ALL | wx.EXPAND, 5)
        self._box_volume_text.SetToolTip(
            lang.get("program_3d_edit.select_tool.box_size_tooltip")
        )

        # Radio buttons for move mode
        move_radio_sizer = wx.BoxSizer(wx.VERTICAL)
        button_sizer.Add(move_radio_sizer, 0, wx.ALL | wx.EXPAND, 5)
        
        self._move_point1_radio = wx.RadioButton(
            self._button_panel,
            label=lang.get("program_3d_edit.select_tool.button_point1"),
            style=wx.RB_GROUP
        )
        self._move_point1_radio.SetToolTip(
            lang.get("program_3d_edit.select_tool.button_point1_tooltip")
        )
        self._move_point1_radio.SetBackgroundColour((160, 215, 145))
        self._move_point1_radio.Disable()
        self._move_point1_radio.Bind(wx.EVT_RADIOBUTTON, self._on_move_target_change)
        self._move_point1_radio.Bind(wx.EVT_ENTER_WINDOW, self._on_tool_ui_hover)
        move_radio_sizer.Add(self._move_point1_radio, 0, wx.ALL, 2)
        
        self._move_point2_radio = wx.RadioButton(
            self._button_panel,
            label=lang.get("program_3d_edit.select_tool.button_point2")
        )
        self._move_point2_radio.SetToolTip(
            lang.get("program_3d_edit.select_tool.button_point2_tooltip")
        )
        self._move_point2_radio.SetBackgroundColour((150, 150, 215))
        self._move_point2_radio.Disable()
        self._move_point2_radio.Bind(wx.EVT_RADIOBUTTON, self._on_move_target_change)
        self._move_point2_radio.Bind(wx.EVT_ENTER_WINDOW, self._on_tool_ui_hover)
        move_radio_sizer.Add(self._move_point2_radio, 0, wx.ALL, 2)
        
        self._move_selection_radio = wx.RadioButton(
            self._button_panel,
            label=lang.get("program_3d_edit.select_tool.button_selection_box")
        )
        self._move_selection_radio.SetToolTip(
            lang.get("program_3d_edit.select_tool.button_selection_box_tooltip")
        )
        self._move_selection_radio.SetBackgroundColour((255, 255, 255))
        self._move_selection_radio.SetValue(True)  # Default selection
        self._move_selection_radio.Disable()
        self._move_selection_radio.Bind(
            wx.EVT_RADIOBUTTON, self._on_move_target_change
        )
        self._move_selection_radio.Bind(wx.EVT_ENTER_WINDOW, self._on_tool_ui_hover)
        move_radio_sizer.Add(self._move_selection_radio, 0, wx.ALL, 2)

        self._button_panel.Bind(wx.EVT_ENTER_WINDOW, self._on_tool_ui_hover)
        self._button_panel.Bind(wx.EVT_CHAR_HOOK, self._on_panel_char_hook)

        self._resize()
    @property
    def name(self) -> str:
        return "Select"

    def bind_events(self):
        super().bind_events()
        self.canvas.Bind(EVT_RENDER_BOX_CHANGE, self._box_renderer_change)
        self.canvas.Bind(EVT_RENDER_BOX_DISABLE_INPUTS, self._disable_inputs)
        self.canvas.Bind(EVT_RENDER_BOX_ENABLE_INPUTS, self._enable_inputs)
        self.canvas.Bind(EVT_SELECTION_CHANGE, self._on_selection_change)
        self.canvas.Bind(EVT_INPUT_PRESS, self._on_input_press)
        self.canvas.Bind(EVT_INPUT_HELD, self._on_input_held)
        self.canvas.Bind(wx.EVT_KEY_DOWN, self._on_canvas_key_down)
        self.canvas.Bind(wx.EVT_SIZE, self._on_resize)
        self._selection.bind_events()
        self._inspect_block.bind_events()

    def enable(self):
        # Preserve current projection mode (2D/3D)
        current_projection = self.canvas.camera.projection_mode
        super().enable()
        self.canvas.camera.projection_mode = current_projection
        
        self._selection.enable()
        self._pull_selection()
        self._button_panel.Show()
        wx.CallAfter(self.canvas.SetFocus)
        self._resize()

    def disable(self):
        super().disable()
        self._button_panel.Hide()

    def _add_spin_ctrl(
        self, label: str, tooltip: str, colour: Tuple[int, int, int]
    ) -> wx.SpinCtrl:
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._button_panel.GetSizer().Add(sizer, 0, wx.EXPAND)
        name_text = wx.StaticText(self._button_panel, label=label)
        sizer.Add(name_text, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        obj = wx.SpinCtrl(
            self._button_panel,
            style=wx.SP_ARROW_KEYS
            | wx.TE_PROCESS_ENTER
            | wx.ALIGN_CENTER_VERTICAL
            | wx.WANTS_CHARS,
            min=-30000000,
            max=30000000,
        )
        sizer.Add(obj, 1, flag=wx.CENTER | wx.TOP | wx.BOTTOM | wx.RIGHT, border=5)
        obj.Bind(wx.EVT_SPINCTRL, self._box_input_change)
        obj.SetValidator(IntValidator())
        obj.Disable()
        obj.SetToolTip(tooltip)
        obj.SetBackgroundColour(colour)
        obj.Bind(wx.EVT_ENTER_WINDOW, self._on_tool_ui_hover)
        return obj

    def _box_input_change(self, _):
        self._selection.active_block_positions = (
            (self._x1.GetValue(), self._y1.GetValue(), self._z1.GetValue()),
            (self._x2.GetValue(), self._y2.GetValue(), self._z2.GetValue()),
        )

    def _box_renderer_change(self, evt: RenderBoxChangeEvent):
        self._update_selection_inputs(*evt.points)
        evt.Skip()

    def _on_selection_change(self, evt):
        self._pull_selection()
        evt.Skip()

    def _pull_selection(self):
        self._update_selection_inputs(*self._selection.active_block_positions)

    def _update_selection_inputs(
        self, point1: BlockCoordinates, point2: BlockCoordinates
    ):
        x1, y1, z1, x2, y2, z2 = map(int, (*point1, *point2))
        self._x1.SetValue(x1)
        self._y1.SetValue(y1)
        self._z1.SetValue(z1)
        self._x2.SetValue(x2)
        self._y2.SetValue(y2)
        self._z2.SetValue(z2)
        xdim = int(abs(x2 - x1))
        ydim = int(abs(y2 - y1))
        zdim = int(abs(z2 - z1))
        self._box_size_selector_text.SetLabel(
            self._box_size_selector_fstring.format(
                x=xdim,
                y=ydim,
                z=zdim,
            )
        )
        self._box_volume_text.SetLabel(
            f"{xdim + 1}x{ydim + 1}x{zdim + 1}={(xdim + 1)*(ydim + 1)*(zdim + 1):,}"
        )
        self._resize()

    def _enable_inputs(self, evt):
        self._set_scroll_state(True)
        self._move_point1_radio.Enable()
        self._move_point2_radio.Enable()
        self._move_selection_radio.Enable()
        evt.Skip()

    def _disable_inputs(self, evt):
        self._set_scroll_state(False)
        self._move_point1_radio.Disable()
        self._move_point2_radio.Disable()
        self._move_selection_radio.Disable()
        evt.Skip()

    def _set_scroll_state(self, state: bool):
        for scroll in (self._x1, self._y1, self._z1, self._x2, self._y2, self._z2):
            scroll.Enable(state)

    def _on_move_target_change(self, evt: wx.CommandEvent):
        wx.CallAfter(self.canvas.SetFocus)
        evt.Skip()

    def _on_tool_ui_hover(self, evt: wx.MouseEvent):
        wx.CallAfter(self.canvas.SetFocus)
        evt.Skip()

    def _on_panel_char_hook(self, evt: wx.KeyEvent):
        if (
            evt.GetKeyCode() == wx.WXK_TAB
            and not evt.ControlDown()
            and not evt.AltDown()
        ):
            if self._navigate_focus(forward=not evt.ShiftDown()):
                return
        evt.Skip()

    def _on_canvas_key_down(self, evt: wx.KeyEvent):
        if (
            evt.GetKeyCode() == wx.WXK_TAB
            and not evt.ControlDown()
            and not evt.AltDown()
            and self._navigate_focus(forward=not evt.ShiftDown())
        ):
            return
        evt.Skip()

    def _navigate_focus(self, forward: bool) -> bool:
        if not self._button_panel.IsShownOnScreen():
            return False

        controls = self._collect_focusable_children(self._button_panel)
        if not controls:
            return False

        focus = wx.Window.FindFocus()
        if focus in controls:
            index = controls.index(focus)
            target_index = (index + (1 if forward else -1)) % len(controls)
        else:
            target_index = 0 if forward else -1

        controls[target_index].SetFocus()
        return True

    def _collect_focusable_children(self, parent: wx.Window):
        controls = []
        for child in parent.GetChildren():
            if isinstance(child, wx.Window):
                if child.IsShownOnScreen() and child.IsEnabled() and child.AcceptsFocus():
                    controls.append(child)
                controls.extend(self._collect_focusable_children(child))
        return controls

    def _find_first_focusable_child(self, parent: wx.Window):
        for child in parent.GetChildren():
            if isinstance(child, wx.Window):
                if child.IsShownOnScreen() and child.IsEnabled() and child.AcceptsFocus():
                    return child
                nested = self._find_first_focusable_child(child)
                if nested is not None:
                    return nested
        return None

    @staticmethod
    def _is_descendant(parent: wx.Window, child: wx.Window) -> bool:
        current = child
        while current is not None:
            if current is parent:
                return True
            current = current.GetParent()
        return False

    def _on_input_press(self, evt: InputPressEvent):
        if evt.action_id == ACT_TOGGLE_MOVE_TARGET:
            self._toggle_move_target()
        elif evt.action_id == ACT_TOGGLE_WASD_MODE:
            self.canvas.wasd_moves_cursor = not self.canvas.wasd_moves_cursor
        elif self.canvas.wasd_moves_cursor:
            if evt.action_id == ACT_LOOK_UP:
                self._rotate_selection_box("x", 1)
            elif evt.action_id == ACT_LOOK_DOWN:
                self._rotate_selection_box("x", -1)
            elif evt.action_id == ACT_LOOK_LEFT:
                self._rotate_selection_box("y", -1)
            elif evt.action_id == ACT_LOOK_RIGHT:
                self._rotate_selection_box("y", 1)
        evt.Skip()

    def _toggle_move_target(self):
        radios = [
            self._move_point1_radio,
            self._move_point2_radio,
            self._move_selection_radio,
        ]
        current_index = 0
        for index, radio in enumerate(radios):
            if radio.GetValue():
                current_index = index
                break
        next_index = (current_index + 1) % len(radios)
        radios[next_index].SetValue(True)

    def _on_input_held(self, evt: InputHeldEvent):
        """Handle cursor movement with arrow keys and page up/down."""
        x = y = z = 0
        wasd_consumed = False

        if ACT_CURSOR_UP in evt.action_ids:
            y += 1
        if ACT_CURSOR_DOWN in evt.action_ids:
            y -= 1
        if ACT_CURSOR_FORWARDS in evt.action_ids:
            z += 1
        if ACT_CURSOR_BACKWARDS in evt.action_ids:
            z -= 1
        if ACT_CURSOR_LEFT in evt.action_ids:
            x += 1
        if ACT_CURSOR_RIGHT in evt.action_ids:
            x -= 1

        # If move cursor mode is enabled, also respond to WASD camera keys
        if self.canvas.wasd_moves_cursor:
            if ACT_MOVE_UP in evt.action_ids:
                y += 1
                wasd_consumed = True
            if ACT_MOVE_DOWN in evt.action_ids:
                y -= 1
                wasd_consumed = True
            if ACT_MOVE_FORWARDS in evt.action_ids:
                z += 1
                wasd_consumed = True
            if ACT_MOVE_BACKWARDS in evt.action_ids:
                z -= 1
                wasd_consumed = True
            if ACT_MOVE_LEFT in evt.action_ids:
                x += 1
                wasd_consumed = True
            if ACT_MOVE_RIGHT in evt.action_ids:
                x -= 1
                wasd_consumed = True

        if any((x, y, z)):
            offset = self._rotate_offset((x, y, z))
            if self._move_point1_radio.GetValue():
                self._move_point1(offset)
            elif self._move_point2_radio.GetValue():
                self._move_point2(offset)
            elif self._move_selection_radio.GetValue():
                self._move_selection(offset)

        # Only skip if we didn't consume WASD keys - this prevents camera movement
        if not wasd_consumed:
            evt.Skip()

    def _rotate_offset(self, offset: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Rotate movement offset based on camera rotation."""
        x, y, z = offset
        ry = self.canvas.camera.rotation[0]
        x, y, z, _ = (
            numpy.round(
                numpy.matmul(
                    rotation_matrix_xy(0, -math.radians(round(ry / 90) * 90)),
                    (x, y, z, 0),
                )
            )
            .astype(int)
            .tolist()
        )
        return x, y, z

    def _move_point1(self, offset: Tuple[int, int, int]):
        ox, oy, oz = offset
        (x, y, z), point2 = self._selection.active_block_positions
        self._selection.active_block_positions = (x + ox, y + oy, z + oz), point2

    def _move_point2(self, offset: Tuple[int, int, int]):
        ox, oy, oz = offset
        point1, (x, y, z) = self._selection.active_block_positions
        self._selection.active_block_positions = point1, (x + ox, y + oy, z + oz)

    def _move_selection(self, offset: Tuple[int, int, int]):
        ox, oy, oz = offset
        (x1, y1, z1), (x2, y2, z2) = self._selection.active_block_positions
        self._selection.active_block_positions = (x1 + ox, y1 + oy, z1 + oz), (
            x2 + ox,
            y2 + oy,
            z2 + oz,
        )

    def _rotate_selection_box(self, axis: str, direction: int):
        p1, p2 = self._selection.active_block_positions

        min_block = numpy.array((
            min(p1[0], p2[0]),
            min(p1[1], p2[1]),
            min(p1[2], p2[2]),
        ), dtype=float)
        max_block = numpy.array((
            max(p1[0], p2[0]),
            max(p1[1], p2[1]),
            max(p1[2], p2[2]),
        ), dtype=float)

        min_corner = min_block
        max_corner = max_block + 1
        center = (min_corner + max_corner) / 2

        corners = numpy.array(
            [
                [x, y, z]
                for x in (min_corner[0], max_corner[0])
                for y in (min_corner[1], max_corner[1])
                for z in (min_corner[2], max_corner[2])
            ],
            dtype=float,
        )
        rel = corners - center

        if axis == "x":
            if direction > 0:
                rel = numpy.column_stack((rel[:, 0], rel[:, 2], -rel[:, 1]))
            else:
                rel = numpy.column_stack((rel[:, 0], -rel[:, 2], rel[:, 1]))
        elif axis == "y":
            if direction > 0:
                rel = numpy.column_stack((rel[:, 2], rel[:, 1], -rel[:, 0]))
            else:
                rel = numpy.column_stack((-rel[:, 2], rel[:, 1], rel[:, 0]))
        else:
            return

        rotated = rel + center
        new_min_corner = numpy.rint(rotated.min(axis=0)).astype(int)
        new_max_corner = numpy.rint(rotated.max(axis=0)).astype(int)

        new_p1 = tuple(new_min_corner.tolist())
        new_p2 = tuple((new_max_corner - 1).tolist())
        self._selection.active_block_positions = new_p1, new_p2

    def _on_resize(self, evt):
        self._resize()
        evt.Skip()

    def _resize(self):
        panel_size = self._button_panel.GetBestSize()
        canvas_height = self.canvas.GetSize().GetHeight()
        allowed_canvas_height = canvas_height - 60
        ideal_path_height = panel_size.GetHeight()
        panel_height = min(ideal_path_height, allowed_canvas_height)
        panel_width = panel_size.GetWidth()
        if allowed_canvas_height < ideal_path_height:
            panel_width += wx.SystemSettings.GetMetric(wx.SYS_VSCROLL_X)
        self._button_panel.SetSize(
            wx.Rect(
                0, canvas_height // 2 - panel_height // 2, panel_width, panel_height
            )
        )
        self._button_panel.Layout()
        self._button_panel.Raise()

    def _draw(self):
        global paint_log_count
        self.canvas.renderer.start_draw()
        if self.canvas.camera.projection_mode == Projection.PERSPECTIVE:
            self.canvas.renderer.draw_sky_box()
            glClear(GL_DEPTH_BUFFER_BIT)
        self.canvas.renderer.draw_level()
        self._selection.draw()
        self.canvas.renderer.end_draw()
        if paint_log_count < 10:
            paint_log_count += 1
            log.debug(f"Painted frame. {paint_log_count}/10")
