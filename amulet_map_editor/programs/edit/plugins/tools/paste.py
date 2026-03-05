import wx
from typing import TYPE_CHECKING, Tuple, Union, Type
import logging
import math
import numpy

from OpenGL.GL import (
    glClear,
    GL_DEPTH_BUFFER_BIT,
)

from amulet.api.data_types import PointCoordinates
from amulet.api.level import BaseLevel
from amulet.api.level.base_level.clone import PasteRule
from amulet.api.structure import structure_cache
from amulet.operations.paste import paste_iter
from amulet.utils.matrix import (
    rotation_matrix_xyz,
    decompose_transformation_matrix,
    scale_matrix,
    transform_matrix,
)

from amulet_map_editor import lang
from amulet_map_editor.api import image
from amulet_map_editor.api.wx.util.validators import IntValidator, FloatValidator
from amulet_map_editor.api.wx.ui.simple import SimpleScrollablePanel
from amulet_map_editor.api.opengl.camera import Projection
from amulet_map_editor.api.opengl.mesh.level import RenderLevel
from amulet_map_editor.programs.edit.api.key_config import (
    ACT_BOX_CLICK,
    ACT_ROTATE_CURSOR_UP,
    ACT_ROTATE_CURSOR_DOWN,
    ACT_ROTATE_CURSOR_LEFT,
    ACT_ROTATE_CURSOR_RIGHT,
    ACT_CURSOR_UP,
    ACT_CURSOR_DOWN,
    ACT_CURSOR_FORWARDS,
    ACT_CURSOR_BACKWARDS,
    ACT_CURSOR_LEFT,
    ACT_CURSOR_RIGHT,
    ACT_FOCUS_PASTE_DIALOG,
    ACT_TOGGLE_WASD_MODE,
    ACT_MOVE_UP,
    ACT_MOVE_DOWN,
    ACT_MOVE_FORWARDS,
    ACT_MOVE_BACKWARDS,
    ACT_MOVE_LEFT,
    ACT_MOVE_RIGHT,
)
from amulet_map_editor.programs.edit.api.operations import OperationSuccessful
from amulet_map_editor.programs.edit.api.ui.tool import DefaultBaseToolUI
from amulet_map_editor.programs.edit.api.behaviour import StaticSelectionBehaviour
from amulet_map_editor.programs.edit.api.behaviour.pointer_behaviour import (
    PointerBehaviour,
    EVT_POINT_CHANGE,
    PointChangeEvent,
)
from amulet_map_editor.programs.edit.api.events import (
    InputPressEvent,
    InputHeldEvent,
    EVT_INPUT_PRESS,
    EVT_INPUT_HELD,
)
from amulet_map_editor.api.opengl.matrix import rotation_matrix_xy

if TYPE_CHECKING:
    from amulet_map_editor.programs.edit.api.canvas import EditCanvas

log = logging.getLogger(__name__)

BottomLeftRight = wx.BOTTOM | wx.LEFT | wx.RIGHT
BottomLeftRightCentre = BottomLeftRight | wx.ALIGN_CENTER_HORIZONTAL
BottomLeftRightExpand = BottomLeftRight | wx.EXPAND


class TupleInput(wx.FlexGridSizer):
    WindowCls: Union[Type[wx.SpinCtrl], Type[wx.SpinCtrlDouble]] = None
    Validator: Type[wx.Validator] = None

    def __init__(
        self,
        parent: wx.Window,
        x_str: str,
        y_str: str,
        z_str: str,
        min_value: int = -30_000_000,
        max_value: int = 30_000_000,
        start_value: int = 0,
        style=wx.SP_ARROW_KEYS,
    ):
        super().__init__(3, 2, 5, 5)

        x_label = wx.StaticText(parent, label=x_str)
        self.Add(x_label, 0, wx.ALIGN_CENTER)
        self.x = self.WindowCls(
            parent, min=min_value, max=max_value, initial=start_value, style=style
        )
        self.x.SetValidator(self.Validator())
        self.Add(self.x, 0, wx.EXPAND)

        y_label = wx.StaticText(parent, label=y_str)
        self.Add(y_label, 0, wx.ALIGN_CENTER)
        self.y = self.WindowCls(
            parent, min=min_value, max=max_value, initial=start_value, style=style
        )
        self.y.SetValidator(self.Validator())
        self.Add(self.y, 0, wx.EXPAND)

        z_label = wx.StaticText(parent, label=z_str)
        self.Add(z_label, 0, wx.ALIGN_CENTER)
        self.z = self.WindowCls(
            parent, min=min_value, max=max_value, initial=start_value, style=style
        )
        self.z.SetValidator(self.Validator())
        self.Add(self.z, 0, wx.EXPAND)
        self.AddGrowableCol(1)

    @property
    def value(self):
        return self.x.GetValue(), self.y.GetValue(), self.z.GetValue()

    @value.setter
    def value(self, value):
        self.x.SetValue(value[0])
        self.y.SetValue(value[1])
        self.z.SetValue(value[2])


class TupleIntInput(TupleInput):
    WindowCls = wx.SpinCtrl
    Validator = IntValidator

    @property
    def value(self) -> Tuple[int, int, int]:
        return self.x.GetValue(), self.y.GetValue(), self.z.GetValue()

    @value.setter
    def value(self, value: Tuple[int, int, int]):
        self.x.SetValue(value[0])
        self.y.SetValue(value[1])
        self.z.SetValue(value[2])


class TupleFloatInput(TupleInput):
    WindowCls = wx.SpinCtrlDouble
    Validator = FloatValidator

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.x.Bind(wx.EVT_MOUSEWHEEL, self._on_wheel)
        self.y.Bind(wx.EVT_MOUSEWHEEL, self._on_wheel)
        self.z.Bind(wx.EVT_MOUSEWHEEL, self._on_wheel)
        self.x.SetIncrement(1)
        self.y.SetIncrement(1)
        self.z.SetIncrement(1)

    @property
    def value(self) -> Tuple[float, float, float]:
        return self.x.GetValue(), self.y.GetValue(), self.z.GetValue()

    @value.setter
    def value(self, value: Tuple[float, float, float]):
        self.x.SetValue(value[0])
        self.y.SetValue(value[1])
        self.z.SetValue(value[2])

    def _on_wheel(self, evt: wx.MouseEvent):
        """Add scroll wheel behaviour to the input."""
        rotation = evt.GetWheelRotation()
        ctrl = evt.GetEventObject()
        if rotation > 0:
            ctrl.SetValue(ctrl.GetValue() + ctrl.GetIncrement())
            self._changed(ctrl)
        elif rotation < 0:
            ctrl.SetValue(ctrl.GetValue() - ctrl.GetIncrement())
            self._changed(ctrl)

    @staticmethod
    def _changed(ctrl: wx.SpinCtrlDouble):
        """Create a changed event for the SpinCtrlDouble."""
        evt = wx.SpinDoubleEvent(wx.wxEVT_SPINCTRLDOUBLE, ctrl.GetId(), ctrl.GetValue())
        evt.SetEventObject(ctrl)
        wx.PostEvent(ctrl, evt)


class RotationTupleInput(TupleFloatInput):
    def __init__(
        self,
        parent: wx.Window,
        x_str: str,
        y_str: str,
        z_str: str,
        increment=90,
    ):
        super().__init__(
            parent, x_str, y_str, z_str, -180, 180, style=wx.SP_ARROW_KEYS | wx.SP_WRAP
        )
        self.increment = increment
        self.x.Bind(wx.EVT_SPINCTRLDOUBLE, self._on_change)
        self.y.Bind(wx.EVT_SPINCTRLDOUBLE, self._on_change)
        self.z.Bind(wx.EVT_SPINCTRLDOUBLE, self._on_change)

    @property
    def value(self) -> Tuple[float, float, float]:
        return self.x.GetValue(), self.y.GetValue(), self.z.GetValue()

    @value.setter
    def value(self, value: Tuple[float, float, float]):
        self.x.SetValue(round(value[0]))
        self.y.SetValue(round(value[1]))
        self.z.SetValue(round(value[2]))

    @property
    def rotation_radians(self) -> Tuple[float, float, float]:
        return (
            math.radians(self.x.GetValue()),
            math.radians(self.y.GetValue()),
            math.radians(self.z.GetValue()),
        )

    @property
    def increment(self) -> int:
        return self.x.GetIncrement()

    @increment.setter
    def increment(self, increment: int):
        assert isinstance(increment, int) and increment >= 1
        self.x.SetIncrement(increment)
        self.y.SetIncrement(increment)
        self.z.SetIncrement(increment)
        self._round_values()

    @staticmethod
    def _on_change(evt: wx.SpinDoubleEvent):
        ctrl = evt.GetEventObject()
        ctrl.SetValue(
            int(round(ctrl.GetValue() / ctrl.GetIncrement())) * ctrl.GetIncrement()
        )
        evt.SetValue(ctrl.GetValue())
        evt.Skip()

    def _round_value(self, ctrl: wx.SpinCtrlDouble):
        ctrl.SetValue(
            int(round(ctrl.GetValue() / ctrl.GetIncrement())) * ctrl.GetIncrement()
        )
        self._changed(ctrl)

    def _round_values(self):
        self._round_value(self.x)
        self._round_value(self.y)
        self._round_value(self.z)


class PasteTool(wx.BoxSizer, DefaultBaseToolUI):
    def __init__(self, canvas: "EditCanvas"):
        wx.BoxSizer.__init__(self, wx.HORIZONTAL)
        DefaultBaseToolUI.__init__(self, canvas)

        self._selection = StaticSelectionBehaviour(self.canvas)
        self._cursor = PointerBehaviour(self.canvas)
        self._is_enabled = False
        self._mouse_grabbed = False

        self._paste_panel = SimpleScrollablePanel(canvas.GetParent())
        self._paste_panel.Hide()
        self._paste_panel.SetBackgroundColour(
            wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
        )
        self._paste_sizer = wx.BoxSizer(wx.VERTICAL)
        self._paste_panel.SetSizer(self._paste_sizer)

        def add_line():
            """add a line to the UI"""
            line = wx.StaticLine(self._paste_panel)
            self._paste_sizer.Add(line, 0, wx.BOTTOM | wx.EXPAND, 5)

        def add_tick_box(name: str, state: bool = True):
            tick = wx.CheckBox(self._paste_panel, label=name)
            tick.SetValue(state)
            self._paste_sizer.Add(
                tick,
                flag=BottomLeftRight,
                border=5,
            )
            return tick

        def add_label(name: str):
            label = wx.StaticText(self._paste_panel, label=name)
            label.SetFont(
                wx.Font(
                    12,
                    wx.FONTFAMILY_DEFAULT,
                    wx.FONTSTYLE_NORMAL,
                    wx.FONTWEIGHT_NORMAL,
                    True,
                )
            )
            self._paste_sizer.Add(label, 0, BottomLeftRightCentre, 5)

        self._paste_sizer.AddSpacer(5)
        add_label(lang.get("program_3d_edit.paste_tool.location_label"))
        self._location = TupleIntInput(
            self._paste_panel,
            lang.get("program_3d_edit.paste_tool.location_x_label"),
            lang.get("program_3d_edit.paste_tool.location_y_label"),
            lang.get("program_3d_edit.paste_tool.location_z_label"),
        )
        self._location.x.SetToolTip(
            lang.get("program_3d_edit.paste_tool.location_x_tooltip")
        )
        self._location.y.SetToolTip(
            lang.get("program_3d_edit.paste_tool.location_y_tooltip")
        )
        self._location.z.SetToolTip(
            lang.get("program_3d_edit.paste_tool.location_z_tooltip")
        )
        self._paste_sizer.Add(
            self._location,
            flag=BottomLeftRightExpand,
            border=5,
        )

        add_line()

        add_label(lang.get("program_3d_edit.paste_tool.rotation_label"))
        self._free_rotation = wx.CheckBox(
            self._paste_panel,
            label=lang.get("program_3d_edit.paste_tool.free_rotation_label"),
        )
        self._free_rotation.SetToolTip(
            lang.get("program_3d_edit.paste_tool.free_rotation_tooltip")
        )
        self._paste_sizer.Add(
            self._free_rotation,
            flag=BottomLeftRight,
            border=5,
        )

        self._rotation = RotationTupleInput(
            self._paste_panel,
            lang.get("program_3d_edit.paste_tool.rotation_x_label"),
            lang.get("program_3d_edit.paste_tool.rotation_y_label"),
            lang.get("program_3d_edit.paste_tool.rotation_z_label"),
        )
        self._rotation.x.SetToolTip(
            lang.get("program_3d_edit.paste_tool.rotation_x_tooltip")
        )
        self._rotation.y.SetToolTip(
            lang.get("program_3d_edit.paste_tool.rotation_y_tooltip")
        )
        self._rotation.z.SetToolTip(
            lang.get("program_3d_edit.paste_tool.rotation_z_tooltip")
        )
        self._paste_sizer.Add(
            self._rotation,
            flag=BottomLeftRightExpand,
            border=5,
        )
        self._free_rotation.Bind(wx.EVT_CHECKBOX, self._on_free_rotation_change)

        rotate_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._paste_sizer.Add(
            rotate_sizer,
            flag=BottomLeftRightCentre,
            border=5,
        )

        self._rotate_left_button = wx.BitmapButton(
            self._paste_panel, bitmap=image.icon.tablericons.rotate_2.bitmap(22, 22)
        )
        self._rotate_left_button.SetToolTip(
            lang.get("program_3d_edit.paste_tool.rotate_anti_clockwise_tooltip")
        )
        self._rotate_left_button.Bind(wx.EVT_BUTTON, self._on_rotate_left)
        rotate_sizer.Add(self._rotate_left_button)

        self._rotate_right_button = wx.BitmapButton(
            self._paste_panel,
            bitmap=image.icon.tablericons.rotate_clockwise_2.bitmap(22, 22),
        )
        self._rotate_right_button.SetToolTip(
            lang.get("program_3d_edit.paste_tool.rotate_clockwise_tooltip")
        )
        self._rotate_right_button.Bind(wx.EVT_BUTTON, self._on_rotate_right)
        rotate_sizer.Add(self._rotate_right_button)

        add_line()

        add_label(lang.get("program_3d_edit.paste_tool.scale_label"))
        self._scale = TupleFloatInput(
            self._paste_panel,
            lang.get("program_3d_edit.paste_tool.scale_x_label"),
            lang.get("program_3d_edit.paste_tool.scale_y_label"),
            lang.get("program_3d_edit.paste_tool.scale_z_label"),
            start_value=1,
        )
        self._scale.x.SetToolTip(lang.get("program_3d_edit.paste_tool.scale_x_tooltip"))
        self._scale.y.SetToolTip(lang.get("program_3d_edit.paste_tool.scale_y_tooltip"))
        self._scale.z.SetToolTip(lang.get("program_3d_edit.paste_tool.scale_z_tooltip"))
        self._scale.x.SetDigits(2)
        self._scale.y.SetDigits(2)
        self._scale.z.SetDigits(2)
        self._paste_sizer.Add(
            self._scale,
            flag=BottomLeftRightExpand,
            border=5,
        )

        self._paste_panel.Bind(wx.EVT_SPINCTRL, self._on_transform_change)
        self._paste_panel.Bind(wx.EVT_SPINCTRLDOUBLE, self._on_transform_change)
        self._paste_panel.Bind(wx.EVT_CHAR_HOOK, self._on_panel_char_hook)

        mirror_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._paste_sizer.Add(
            mirror_sizer,
            flag=BottomLeftRightCentre,
            border=5,
        )

        # the tablericons file names are the wrong way around
        self._mirror_horizontal_button = wx.BitmapButton(
            self._paste_panel,
            bitmap=image.icon.tablericons.flip_vertical.bitmap(22, 22),
        )
        self._mirror_horizontal_button.SetToolTip(
            lang.get("program_3d_edit.paste_tool.mirror_horizontal_tooltip")
        )
        self._mirror_horizontal_button.Bind(wx.EVT_BUTTON, self._on_mirror_horizontal)
        mirror_sizer.Add(self._mirror_horizontal_button)

        self._mirror_vertical_button = wx.BitmapButton(
            self._paste_panel,
            bitmap=image.icon.tablericons.flip_horizontal.bitmap(22, 22),
        )
        self._mirror_vertical_button.SetToolTip(
            lang.get("program_3d_edit.paste_tool.mirror_vertical_tooltip")
        )
        self._mirror_vertical_button.Bind(wx.EVT_BUTTON, self._on_mirror_vertical)
        mirror_sizer.Add(self._mirror_vertical_button)

        add_line()

        self._copy_air = add_tick_box(
            lang.get("program_3d_edit.paste_tool.copy_air_label")
        )
        self._copy_air.SetToolTip(
            lang.get("program_3d_edit.paste_tool.copy_air_tooltip")
        )
        self._copy_water = add_tick_box(
            lang.get("program_3d_edit.paste_tool.copy_water_label")
        )
        self._copy_water.SetToolTip(
            lang.get("program_3d_edit.paste_tool.copy_water_tooltip")
        )
        self._copy_lava = add_tick_box(
            lang.get("program_3d_edit.paste_tool.copy_lava_label")
        )
        self._copy_lava.SetToolTip(
            lang.get("program_3d_edit.paste_tool.copy_lava_tooltip")
        )

        self._paste_rule = wx.Choice(
            self._paste_panel,
            choices=[
                lang.get("program_3d_edit.paste_tool.paste_all"),
                lang.get("program_3d_edit.paste_tool.paste_existing"),
                lang.get("program_3d_edit.paste_tool.paste_not_existing"),
            ],
        )
        self._paste_rule.SetSelection(0)
        self._paste_sizer.Add(
            self._paste_rule,
            flag=BottomLeftRightExpand,
            border=5,
        )

        add_line()

        confirm_button = wx.Button(self._paste_panel, label="Confirm")
        self._paste_sizer.Add(confirm_button, 0, BottomLeftRightExpand, 5)
        confirm_button.Bind(wx.EVT_BUTTON, self._paste_confirm)

        self._paste_panel.Disable()
        self._resize()

    @property
    def name(self) -> str:
        return "Paste"

    def bind_events(self):
        super().bind_events()
        self._selection.bind_events()
        self._cursor.bind_events()
        self.canvas.Bind(EVT_POINT_CHANGE, self._on_pointer_change)
        self.canvas.Bind(EVT_INPUT_PRESS, self._on_input_press)
        self.canvas.Bind(EVT_INPUT_HELD, self._on_input_held)
        self.canvas.Bind(wx.EVT_KEY_DOWN, self._on_canvas_key_down)
        self.canvas.Bind(wx.EVT_SIZE, self._on_resize)

    def enable(self):
        # Preserve current projection mode (2D/3D)
        current_projection = self.canvas.camera.projection_mode
        super().enable()
        self.canvas.camera.projection_mode = current_projection
        
        self._selection.update_selection()
        self._paste_panel.Show()
        wx.CallAfter(self.canvas.SetFocus)
        self._resize()

    def set_state(self, state):
        if (
            isinstance(state, dict)
            and isinstance(state.get("structure"), BaseLevel)
            and isinstance(state.get("dimension"), str)
        ):
            structure = state["structure"]
            dimension = state["dimension"]
        elif structure_cache:
            structure, dimension = structure_cache.get_structure()
        else:
            wx.MessageBox("A structure needs to be copied before one can be pasted.")
            return

        self._paste_panel.Enable()
        self._is_enabled = True
        self._mouse_grabbed = False

        camera_x, camera_y, camera_z = self.canvas.camera.location
        yaw, pitch = self.canvas.camera.rotation
        yaw_rad = math.radians(yaw)
        pitch_rad = math.radians(pitch)

        forward_x = math.cos(pitch_rad) * math.sin(yaw_rad)
        forward_y = -math.sin(pitch_rad)
        forward_z = math.cos(pitch_rad) * math.cos(yaw_rad)

        paste_location = (
            int(round(camera_x + forward_x * 5)),
            int(round(camera_y + forward_y * 5 - 2)),
            int(round(camera_z + forward_z * 5)),
        )
        
        # Clear and add the structure with the correct location
        self.canvas.renderer.fake_levels.clear()
        self.canvas.renderer.fake_levels.append(
            structure, dimension, paste_location, (1, 1, 1), (0, 0, 0)
        )
        
        # Now enable manual cursor mode and sync positions
        self._cursor._manual_cursor_mode = True
        self._cursor._manual_cursor_pos = list(paste_location)
        self._cursor._pointer_moved = True
        
        # Update UI to show the location
        self._location.value = paste_location

    def disable(self):
        super().disable()
        self._paste_panel.Disable()
        self._is_enabled = False
        self._mouse_grabbed = False
        self.canvas.renderer.fake_levels.clear()
        self._paste_panel.Hide()
        
        # Exit manual cursor mode
        self._cursor._manual_cursor_mode = False

    @property
    def location(self) -> PointCoordinates:
        """The location as specified in the UI."""
        return self._location.value

    @location.setter
    def location(self, location: PointCoordinates):
        """Set the location value.
        Will update the UI and the renderer."""
        self._location.value = location
        self._update_transform()
        
        # Update manual cursor position to match paste location (use actual UI values)
        if self._cursor._manual_cursor_mode:
            self._cursor._manual_cursor_pos = list(self._location.value)
            self._cursor._pointer_moved = True

    def _on_free_rotation_change(self, evt):
        if self._free_rotation.GetValue():
            self._rotation.increment = 1
        else:
            self._rotation.increment = 90

    def _on_rotate_left(self, evt):
        self._rotate(-90)

    def _on_rotate_right(self, evt):
        self._rotate(90)

    def _rotate(self, angle: int):
        """Rotate the floating selection by the angle based on the camera rotation."""
        angle = math.radians(angle)
        ry, rx = self.canvas.camera.rotation
        if rx < -45:
            rotation_change = rotation_matrix_xyz(0, angle, 0)
        elif -45 <= rx < 45:
            if -135 <= ry < -45:
                # east
                rotation_change = rotation_matrix_xyz(angle, 0, 0)
            elif -45 <= ry < 45:
                # south
                rotation_change = rotation_matrix_xyz(0, 0, angle)
            elif 45 <= ry < 135:
                # west
                rotation_change = rotation_matrix_xyz(-angle, 0, 0)
            else:
                # north
                rotation_change = rotation_matrix_xyz(0, 0, -angle)
        else:
            rotation_change = rotation_matrix_xyz(0, -angle, 0)

        self._rotation.value = numpy.rad2deg(
            decompose_transformation_matrix(
                numpy.matmul(
                    rotation_change, rotation_matrix_xyz(*self._rotation_radians())
                )
            )[1]
        )
        self._update_transform()

    def _rotation_radians(self) -> Tuple[float, float, float]:
        return tuple(math.radians(v) for v in self._rotation.value)

    def _on_mirror_vertical(self, evt):
        ry, rx = self.canvas.camera.rotation
        if -45 <= rx < 45:
            # looking north, east, south or west vertical mirror is always in y
            self._mirror(1)
        elif -135 <= ry < -45 or 45 <= ry < 135:
            # looking down or up facing east or west
            self._mirror(0)
        else:
            # looking down or up facing north or south
            self._mirror(2)

    def _on_mirror_horizontal(self, evt):
        ry, rx = self.canvas.camera.rotation
        if -135 <= ry < -45 or 45 <= ry < 135:
            # facing east or west
            self._mirror(2)
        else:
            # facing north or south
            self._mirror(0)

    def _mirror(self, axis: int):
        """Mirror the selection in the given axis.

        :param axis: The axis to scale in 0=x, 1=y, 2=z
        :return:
        """
        scale = [(-1, 1, 1), (1, -1, 1), (1, 1, -1)][axis]
        self._scale.value, rotation, _ = decompose_transformation_matrix(
            numpy.matmul(
                scale_matrix(*scale),
                transform_matrix(
                    self._scale.value, self._rotation_radians(), (0, 0, 0)
                ),
            )
        )
        self._rotation.value = numpy.rad2deg(rotation)
        self._update_transform()

    def _on_pointer_change(self, evt: PointChangeEvent):
        if self._is_enabled and self._mouse_grabbed:
            self.location = evt.point
        evt.Skip()

    def _on_input_press(self, evt: InputPressEvent):
        if self._is_enabled and evt.action_id == ACT_BOX_CLICK:
            if self._mouse_grabbed:
                self._mouse_grabbed = False
                self._cursor._manual_cursor_mode = True
                self._cursor._manual_cursor_pos = list(self.location)
                self._cursor._pointer_moved = True
            else:
                self._mouse_grabbed = True
                self._cursor._manual_cursor_mode = False
                self._cursor._pointer_moved = True
                self._cursor._update_pointer()
                self.location = tuple(self._cursor.pointer_base.tolist())
        elif self._is_enabled and evt.action_id == ACT_FOCUS_PASTE_DIALOG:
            self._paste_panel.SetFocus()
            self._location.x.SetFocus()
        elif self._is_enabled and evt.action_id == ACT_TOGGLE_WASD_MODE:
            self.canvas.wasd_moves_cursor = not self.canvas.wasd_moves_cursor
        elif self._is_enabled and evt.action_id == ACT_ROTATE_CURSOR_UP:
            self._rotate_axis("x", 1)
        elif self._is_enabled and evt.action_id == ACT_ROTATE_CURSOR_DOWN:
            self._rotate_axis("x", -1)
        elif self._is_enabled and evt.action_id == ACT_ROTATE_CURSOR_LEFT:
            self._rotate_axis("y", -1)
        elif self._is_enabled and evt.action_id == ACT_ROTATE_CURSOR_RIGHT:
            self._rotate_axis("y", 1)
        evt.Skip()

    def _rotate_axis(self, axis: str, direction: int):
        angle = math.radians(90 * direction)
        if axis == "x":
            rotation_change = rotation_matrix_xyz(angle, 0, 0)
        elif axis == "y":
            rotation_change = rotation_matrix_xyz(0, angle, 0)
        else:
            return

        self._rotation.value = numpy.rad2deg(
            decompose_transformation_matrix(
                numpy.matmul(rotation_change, rotation_matrix_xyz(*self._rotation_radians()))
            )[1]
        )
        self._update_transform()

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
        if not self._paste_panel.IsShownOnScreen():
            return False

        controls = self._collect_focusable_children(self._paste_panel)
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

    def _on_transform_change(self, evt):
        self._update_transform()
        evt.Skip()

    def _update_transform(self):
        """Update the renderer with the new values."""
        self.canvas.renderer.fake_levels.active_transform = (
            self._location.value,
            self._scale.value,
            self._rotation_radians(),
        )

    def _on_input_held(self, evt: InputHeldEvent):
        if not self._is_enabled:
            evt.Skip()
            return

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
            self._mouse_grabbed = False
            self._cursor._manual_cursor_mode = True
            self._cursor._manual_cursor_pos = list(self.location)
            ox, oy, oz = self._rotate_offset((x, y, z))
            lx, ly, lz = self.location
            self.location = lx + ox, ly + oy, lz + oz
            
            # Update manual cursor position to match paste location
            self._cursor._manual_cursor_pos[0] += ox
            self._cursor._manual_cursor_pos[1] += oy
            self._cursor._manual_cursor_pos[2] += oz
            self._cursor._pointer_moved = True

        # Only skip if we didn't consume WASD keys - this prevents camera movement
        if not wasd_consumed:
            evt.Skip()

    def _rotate_offset(self, offset: Tuple[int, int, int]) -> Tuple[int, int, int]:
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

    def _paste_operation(self):
        if all(self._scale.value):
            fake_levels = self.canvas.renderer.fake_levels
            level_index: int = fake_levels.active_level_index
            if level_index is not None:
                render_level: RenderLevel = fake_levels.render_levels[level_index]
                paste_rule = {
                    1: PasteRule.PasteExist,
                    2: PasteRule.PasteNotExist,
                }.get(self._paste_rule.GetSelection(), PasteRule.PasteAll)
                yield from paste_iter(
                    self.canvas.world,
                    self.canvas.dimension,
                    render_level.level,
                    render_level.dimension,
                    self._location.value,
                    self._scale.value,
                    self._rotation.value,
                    self._copy_air.GetValue(),
                    self._copy_water.GetValue(),
                    self._copy_lava.GetValue(),
                    paste_rule,
                )
        else:
            raise OperationSuccessful(
                lang.get("program_3d_edit.paste_tool.zero_scale_message")
            )

    def _paste_confirm(self, evt):
        self.confirm_paste()

    def confirm_paste(self) -> None:
        self.canvas.run_operation(self._paste_operation)

    def _on_resize(self, evt):
        self._resize()
        evt.Skip()

    def _resize(self):
        panel_size = self._paste_panel.GetBestSize()
        canvas_height = self.canvas.GetSize().GetHeight()
        allowed_canvas_height = canvas_height - 60
        ideal_path_height = panel_size.GetHeight()
        panel_height = min(ideal_path_height, allowed_canvas_height)
        panel_width = panel_size.GetWidth()
        if allowed_canvas_height < ideal_path_height:
            panel_width += wx.SystemSettings.GetMetric(wx.SYS_VSCROLL_X)
        self._paste_panel.SetSize(
            wx.Rect(
                0, canvas_height // 2 - panel_height // 2, panel_width, panel_height
            )
        )
        self._paste_panel.Layout()
        self._paste_panel.Raise()
        self._paste_panel.Refresh(False)

    def _draw(self):
        self.canvas.renderer.start_draw()
        if self.canvas.camera.projection_mode == Projection.PERSPECTIVE:
            self.canvas.renderer.draw_sky_box()
            glClear(GL_DEPTH_BUFFER_BIT)
        self.canvas.renderer.draw_level()
        self.canvas.renderer.draw_fake_levels()
        self._selection.draw()
        self.canvas.renderer.end_draw()
