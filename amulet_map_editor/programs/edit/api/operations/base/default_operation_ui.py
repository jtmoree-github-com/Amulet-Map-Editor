from typing import TYPE_CHECKING, Optional
import logging
import wx
from OpenGL.GL import (
    glClear,
    GL_DEPTH_BUFFER_BIT,
)

from .operation_ui import OperationUI
from amulet_map_editor.programs.edit.api.behaviour import StaticSelectionBehaviour
from amulet_map_editor.api.opengl.camera import Projection
from amulet_map_editor.programs.edit.api.behaviour import (
    CameraBehaviour,
    PointerBehaviour,
)
from amulet_map_editor.programs.edit.api.events import (
    InputPressEvent,
    EVT_INPUT_PRESS,
)
from amulet_map_editor.api.wx.util.key_config import (
    serialise_key,
    Shift,
    Control,
    Alt,
)
from amulet_map_editor.programs.edit.api.key_config import (
    ACT_BOX_CLICK,
)

if TYPE_CHECKING:
    from amulet_map_editor.programs.edit.api.canvas import EditCanvas
    from amulet.api.level import BaseLevel


log = logging.getLogger(__name__)


class DefaultOperationUI(OperationUI):
    """An extension of the base OperationUI that adds camera, static selection and some other controls."""

    def __init__(
        self,
        parent: wx.Window,
        canvas: "EditCanvas",
        world: "BaseLevel",
        options_path: str,
    ):
        super().__init__(parent, canvas, world, options_path)
        self._selection = StaticSelectionBehaviour(self.canvas)
        self._camera_behaviour = CameraBehaviour(self.canvas)
        self._pointer = PointerBehaviour(self.canvas)
        self._show_pointer = False

    def enable(self):
        # Preserve current projection mode (2D/3D)
        current_projection = self.canvas.camera.projection_mode
        self._selection.update_selection()
        self.canvas.camera.projection_mode = current_projection

    def bind_events(self):
        self._selection.bind_events()
        self.canvas.Bind(wx.EVT_PAINT, self._on_draw)
        self._camera_behaviour.bind_events()
        self._pointer.bind_events()
        self.canvas.Bind(EVT_INPUT_PRESS, self._on_input_press)
        self.canvas.Bind(wx.EVT_KEY_DOWN, self._on_canvas_key_down)
        if isinstance(self, wx.Window):
            self.Bind(wx.EVT_CHAR_HOOK, self._on_char_hook)

    def _on_canvas_key_down(self, evt: wx.KeyEvent):
        key_code = evt.GetKeyCode()
        if (
            evt.ControlDown()
            and not evt.AltDown()
            and key_code in (ord("R"), ord("r"))
            and self._trigger_run_operation_button()
        ):
            return
        if (
            evt.ControlDown()
            and not evt.AltDown()
            and key_code in (ord("F"), ord("f"))
            and self._focus_first_search_field()
        ):
            return
        evt.Skip()

    def _on_char_hook(self, evt: wx.KeyEvent):
        key_code = evt.GetKeyCode()
        if (
            evt.ControlDown()
            and not evt.AltDown()
            and key_code in (ord("R"), ord("r"))
            and self._trigger_run_operation_button()
        ):
            return
        if (
            key_code == wx.WXK_TAB
            and evt.ShiftDown()
            and not evt.ControlDown()
            and not evt.AltDown()
        ):
            focus = wx.Window.FindFocus()
            if focus is not None and focus.Navigate(wx.NavigationKeyEvent.IsForward):
                return
        if self._dispatch_function_key_from_focused_field(evt):
            return
        if (
            evt.ControlDown()
            and not evt.AltDown()
            and key_code in (ord("F"), ord("f"))
            and self._focus_first_search_field()
        ):
            return
        evt.Skip()

    def _focus_first_search_field(self) -> bool:
        if not isinstance(self, wx.Window):
            return False
        search_ctrl = self._find_search_ctrl(self)
        if search_ctrl is None:
            return False
        search_ctrl.SetFocus()
        search_ctrl.SelectAll()
        return True

    def _trigger_run_operation_button(self) -> bool:
        run_button = getattr(self, "_run_button", None)
        if not isinstance(run_button, wx.Button) or not run_button.IsEnabled():
            return False

        command_event = wx.CommandEvent(wx.wxEVT_BUTTON, run_button.GetId())
        command_event.SetEventObject(run_button)
        run_button.GetEventHandler().ProcessEvent(command_event)
        return True

    def _dispatch_function_key_from_focused_field(self, evt: wx.KeyEvent) -> bool:
        key_code = evt.GetKeyCode()
        if not (wx.WXK_F1 <= key_code <= wx.WXK_F24):
            return False

        key = serialise_key(evt)
        if key is None:
            return False

        buttons = self.canvas.buttons
        original_pressed_keys = buttons._pressed_keys.copy()
        try:
            simulated_pressed_keys = original_pressed_keys.copy()
            if evt.ShiftDown():
                simulated_pressed_keys.add(Shift)
            if evt.ControlDown():
                simulated_pressed_keys.add(Control)
            if evt.AltDown():
                simulated_pressed_keys.add(Alt)

            buttons._pressed_keys = simulated_pressed_keys
            action_ids = buttons._find_actions(key)
        finally:
            buttons._pressed_keys = original_pressed_keys

        if not action_ids:
            return False

        for action_id in action_ids:
            wx.PostEvent(self.canvas, InputPressEvent(action_id))
        return True

    def _find_search_ctrl(self, parent: wx.Window) -> Optional[wx.SearchCtrl]:
        for child in parent.GetChildren():
            if isinstance(child, wx.SearchCtrl):
                return child
            if isinstance(child, wx.Window):
                nested = self._find_search_ctrl(child)
                if nested is not None:
                    return nested
        return None

    def _on_draw(self, evt):
        try:
            self.canvas.SetCurrent(self.canvas.context)
            self._draw()
        except Exception as e:
            log.exception(f"Failed painting: {e}")

    def _draw(self):
        self.canvas.renderer.start_draw()
        if self.canvas.camera.projection_mode == Projection.PERSPECTIVE:
            self.canvas.renderer.draw_sky_box()
            glClear(GL_DEPTH_BUFFER_BIT)
        self.canvas.renderer.draw_level()
        self._selection.draw()
        if self._show_pointer:
            self._pointer.draw()
        self.canvas.renderer.end_draw()

    def _on_input_press(self, evt: InputPressEvent):
        if evt.action_id == ACT_BOX_CLICK:
            self._on_box_click()
        evt.Skip()

    def _on_box_click(self):
        pass
