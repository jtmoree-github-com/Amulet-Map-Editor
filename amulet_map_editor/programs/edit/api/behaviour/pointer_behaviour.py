from typing import TYPE_CHECKING, Type
import wx
import numpy

from amulet_map_editor.api.opengl.mesh.selection.box.render_selection_pointer import (
    RenderSelectionPointer,
)
from amulet_map_editor.api.opengl.mesh.selection.box.render_selection import (
    RenderSelection,
)
from amulet_map_editor.api.opengl.camera import Projection
from amulet.api.data_types import BlockCoordinatesNDArray, BlockCoordinates

from .raycast_behaviour import RaycastBehaviour
from ..events import (
    EVT_PRE_DRAW,
    EVT_CAMERA_MOVED,
    InputPressEvent,
    InputHeldEvent,
    EVT_INPUT_PRESS,
    EVT_INPUT_HELD,
)
from ..key_config import (
    ACT_INCR_SELECT_DISTANCE,
    ACT_DECR_SELECT_DISTANCE,
    ACT_CURSOR_UP,
    ACT_CURSOR_DOWN,
    ACT_CURSOR_FORWARDS,
    ACT_CURSOR_BACKWARDS,
    ACT_CURSOR_LEFT,
    ACT_CURSOR_RIGHT,
)

if TYPE_CHECKING:
    from amulet_map_editor.programs.edit.api.canvas import EditCanvas

_PointChangeEventType = wx.NewEventType()
EVT_POINT_CHANGE = wx.PyEventBinder(_PointChangeEventType)


class PointChangeEvent(wx.PyEvent):
    """Run when the cursor point changed."""

    def __init__(self, point: BlockCoordinates):
        wx.PyEvent.__init__(self, eventType=_PointChangeEventType)
        self._point = point

    @property
    def point(self) -> BlockCoordinates:
        return self._point


class PointerBehaviour(RaycastBehaviour):
    """Adds the behaviour of the selection pointer."""

    def __init__(
        self,
        canvas: "EditCanvas",
        render_selection_cls: Type[RenderSelection] = RenderSelectionPointer,
        allow_keyboard_control: bool = True,
    ):
        super().__init__(canvas)

        # has the pointer moved
        self._pointer_moved = True

        # the distance between the camera and the pointer
        self._pointer_distance = 10

        # manual cursor control
        self._manual_cursor_mode = False
        self._manual_cursor_pos = [0, 0, 0]  # x, y, z position
        self._allow_keyboard_control = allow_keyboard_control

        # the pointer
        self._pointer = render_selection_cls(
            self.canvas.context_identifier,
            self.canvas.renderer.opengl_resource_pack,
        )

    @property
    def pointer_base(self) -> BlockCoordinatesNDArray:
        return self._pointer.point1

    def bind_events(self):
        super().bind_events()
        self.canvas.Bind(EVT_PRE_DRAW, self._pre_draw)
        self.canvas.Bind(EVT_CAMERA_MOVED, self._invalidate_pointer)
        self.canvas.Bind(wx.EVT_MOTION, self._invalidate_pointer)
        if self._allow_keyboard_control:
            self.canvas.Bind(EVT_INPUT_PRESS, self._on_input_press)
            self.canvas.Bind(EVT_INPUT_HELD, self._on_input_held)

    def _on_input_press(self, evt: InputPressEvent):
        if evt.action_id == ACT_INCR_SELECT_DISTANCE:
            self._pointer_distance += 1
            self._pointer_moved = True
        elif evt.action_id == ACT_DECR_SELECT_DISTANCE:
            self._pointer_distance -= 1
            self._pointer_moved = True
        evt.Skip()

    def _on_input_held(self, evt: InputHeldEvent):
        """Handle cursor movement with arrow keys and page up/down."""
        cursor_moved = False
        
        # Check if any cursor movement keys are held
        if ACT_CURSOR_UP in evt.action_ids:
            self._manual_cursor_pos[1] += 1
            cursor_moved = True
        if ACT_CURSOR_DOWN in evt.action_ids:
            self._manual_cursor_pos[1] -= 1
            cursor_moved = True
        if ACT_CURSOR_FORWARDS in evt.action_ids:
            self._manual_cursor_pos[2] -= 1
            cursor_moved = True
        if ACT_CURSOR_BACKWARDS in evt.action_ids:
            self._manual_cursor_pos[2] += 1
            cursor_moved = True
        if ACT_CURSOR_LEFT in evt.action_ids:
            self._manual_cursor_pos[0] -= 1
            cursor_moved = True
        if ACT_CURSOR_RIGHT in evt.action_ids:
            self._manual_cursor_pos[0] += 1
            cursor_moved = True
        
        if cursor_moved:
            # Switch to manual cursor mode
            if not self._manual_cursor_mode:
                # Initialize manual cursor position from current pointer position
                x, y, z = self._pointer.point1.tolist()
                self._manual_cursor_pos = [x, y, z]
                self._manual_cursor_mode = True
            self._pointer_moved = True
        
        evt.Skip()

    def _invalidate_pointer(self, evt):
        # Mouse movement exits manual cursor mode
        if evt.GetEventType() == wx.EVT_MOTION.typeId:
            self._manual_cursor_mode = False
        self._pointer_moved = True
        evt.Skip()

    def _pre_draw(self, evt):
        if self._pointer_moved:
            self._update_pointer()
            self._pointer_moved = False
        evt.Skip()

    def _post_change_event(self):
        x, y, z = self._pointer.point1.tolist()
        wx.PostEvent(self.canvas, PointChangeEvent((x, y, z)))

    def _update_pointer(self):
        """Update the pointer location."""
        if self._manual_cursor_mode:
            # Use manual cursor position
            location = self._manual_cursor_pos
        elif self.canvas.camera.projection_mode == Projection.TOP_DOWN:
            location = self.closest_block_2d()[0]
        else:
            if self.canvas.camera.rotating:
                location = self.distance_block_3d(self._pointer_distance)
            else:
                location = self.closest_block_3d()[0]

        location = numpy.array(location)
        self._pointer.point1, self._pointer.point2 = location, location + 1
        self._post_change_event()

    def draw(self):
        self._pointer.draw(self.canvas.camera.transformation_matrix)
