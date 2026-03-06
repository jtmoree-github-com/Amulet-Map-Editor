import logging
import warnings
import wx
import math
import webbrowser
from typing import Callable, TYPE_CHECKING, Any, Generator, Optional
from types import GeneratorType
from threading import RLock, Thread

from .base_edit_canvas import BaseEditCanvas
from ...edit import EDIT_CONFIG_ID
from ..key_config import (
    DefaultKeybindGroupId,
    KeyboardPresets,
    MousePresets,
    KeybindGroup,
    KeyboardKeys,
    MouseKeys,
    ACT_PASTE,
    ACT_HELP,
    ACT_SAVE_ALL,
    ACT_SAVE_ALL_CLOSE,
    ACT_QUIT_WITHOUT_SAVE,
    ACT_SWITCH_TO_SELECT_MODE,
    ACT_SWITCH_TO_PASTE_MODE,
    ACT_SWITCH_TO_FILL_MODE,
    ACT_SWITCH_TO_WATERLOG_MODE,
    ACT_SWITCH_TO_CLONE_MODE,
    ACT_SWITCH_TO_REPLACE_MODE,
    ACT_SWITCH_TO_BIOME_MODE,
    ACT_SWITCH_TO_IMPORT_MODE,
    ACT_SWITCH_TO_EXPORT_MODE,
    ACT_SWITCH_TO_CHUNK_MODE,
    ACT_TOGGLE_FULLSCREEN,
    ACT_MOVE_CAMERA_TO_CURSOR,
    ACT_TELEPORT_CURSOR_TO_CAMERA,
    ACT_BOX_CLICK_KEY,
    ACT_CLEAR_START_HIGHLIGHT_BOX_ACTION,
    ACT_BOX_CLICK_ADD_KEY,
    ACT_BOX_CLICK,
    ACT_BOX_CLICK_ADD,
    ACT_TOGGLE_MOVE_TARGET,
    ACT_TOGGLE_WASD_MODE,
    ACT_DESELECT_ALL_BOXES,
    ACT_DESELECT_BOX,
    ACT_INSPECT_POINT_1,
    ACT_INSPECT_BLOCK,
    ACT_INCR_SELECT_DISTANCE,
    ACT_DECR_SELECT_DISTANCE,
    ACT_INCR_SPEED,
    ACT_DECR_SPEED,
    ACT_ZOOM_IN,
    ACT_ZOOM_OUT,
    DOT,
    COMMA,
    Alt,
    Up,
    Down,
    Left,
    Right,
    W,
    A,
    S,
    D,
    ACT_LOOK_UP,
    ACT_LOOK_DOWN,
    ACT_LOOK_LEFT,
    ACT_LOOK_RIGHT,
)

import time
import traceback

from amulet.api.data_types import OperationReturnType, OperationYieldType, Dimension
from amulet.api.structure import structure_cache
from amulet.api.level import BaseLevel

from amulet_map_editor import CONFIG
from amulet_map_editor import close_level
from amulet_map_editor.api.wx.ui.traceback_dialog import TracebackDialog
from amulet_map_editor.programs.edit.api.ui.goto import show_goto
from amulet_map_editor.programs.edit.api.ui.tool_manager import ToolManagerSizer
from amulet_map_editor.programs.edit.plugins.tools import PasteTool, SelectTool
from amulet_map_editor.programs.edit.api.operations.errors import (
    OperationError,
    OperationSilentAbort,
    BaseLoudException,
    BaseSilentException,
)
from amulet_map_editor.programs.edit.plugins.operations.stock_plugins.internal_operations import (
    cut,
    copy,
    delete,
)

from amulet_map_editor.programs.edit.api.events import (
    InputPressEvent,
    EVT_INPUT_PRESS,
    UndoEvent,
    RedoEvent,
    CreateUndoEvent,
    SaveEvent,
    ToolChangeEvent,
    EVT_EDIT_CLOSE,
)
from amulet_map_editor.programs.edit.api.ui.file import FilePanel

if TYPE_CHECKING:
    from amulet.api.level import BaseLevel

log = logging.getLogger(__name__)
OperationType = Callable[[], OperationReturnType]


SELECT_MODE_ACTIONS = {
    ACT_CLEAR_START_HIGHLIGHT_BOX_ACTION,
    ACT_BOX_CLICK_KEY,
    ACT_BOX_CLICK_ADD_KEY,
    ACT_TOGGLE_MOVE_TARGET,
    ACT_DESELECT_ALL_BOXES,
    ACT_DESELECT_BOX,
    ACT_INSPECT_POINT_1,
    ACT_INCR_SELECT_DISTANCE,
    ACT_DECR_SELECT_DISTANCE,
}


def show_loading_dialog(
    run: OperationType, title: str, message: str, parent: wx.Window
) -> Any:
    warnings.warn("show_loading_dialog is depreciated.", DeprecationWarning)
    dialog = wx.ProgressDialog(
        title,
        message,
        maximum=10_000,
        parent=parent,
        style=wx.PD_APP_MODAL
        | wx.PD_ELAPSED_TIME
        | wx.PD_REMAINING_TIME
        | wx.PD_AUTO_HIDE,
    )
    dialog.Fit()
    t = time.time()
    try:
        obj = run()
        if isinstance(obj, GeneratorType):
            try:
                while True:
                    progress = next(obj)
                    if isinstance(progress, (list, tuple)):
                        if len(progress) >= 2:
                            message = progress[1]
                        if len(progress) >= 1:
                            progress = progress[0]
                    if isinstance(progress, (int, float)) and isinstance(message, str):
                        dialog.Update(
                            min(9999, max(0, int(progress * 10_000))), message
                        )
                    wx.Yield()
            except StopIteration as e:
                obj = e.value
    except Exception as e:
        dialog.Update(10_000)
        raise e
    time.sleep(max(0.2 - time.time() + t, 0))
    dialog.Update(10_000)
    return obj


class OperationThread(Thread):
    # The operation to run
    _operation: OperationType

    # Should the operation be stopped. Set externally
    stop: bool
    # The starting message for the progress dialog
    message: str
    # The operation progress (from 0-1)
    progress: float
    # The return value from the operation
    out: Any
    # The error raised if any
    error: Optional[BaseException]

    def __init__(self, operation: OperationType, message: str):
        super().__init__()
        self._operation = operation
        self.stop = False
        self.message = message
        self.progress = 0.0
        self.out = None
        self.error = None

    def run(self) -> None:
        t = time.time()
        try:
            obj = self._operation()
            if isinstance(obj, GeneratorType):
                try:
                    while True:
                        if self.stop:
                            raise OperationSilentAbort
                        progress = next(obj)
                        if isinstance(progress, (list, tuple)):
                            if len(progress) >= 2:
                                self.message = progress[1]
                            if len(progress) >= 1:
                                self.progress = progress[0]
                        elif isinstance(progress, (int, float)):
                            self.progress = progress
                except StopIteration as e:
                    self.out = e.value
        except BaseException as e:
            self.error = e
        time.sleep(max(0.2 - time.time() + t, 0))


class EditCanvas(BaseEditCanvas):
    def __init__(self, parent: wx.Window, world: "BaseLevel"):
        super().__init__(parent, world)
        self._file_panel: Optional[FilePanel] = None
        self._tool_sizer: Optional[ToolManagerSizer] = None
        self.buttons.register_actions(self.key_binds)
        self.buttons.register_action(ACT_INCR_SPEED, tuple(), DOT)
        self.buttons.register_action(ACT_DECR_SPEED, tuple(), COMMA)
        self.buttons.register_action(ACT_ZOOM_IN, tuple(), DOT)
        self.buttons.register_action(ACT_ZOOM_OUT, tuple(), COMMA)

        self._canvas_sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self._canvas_sizer)

        # Tracks if an operation has been started and not finished.
        self._operation_running = False
        # This lock stops two threads from editing the world simultaneously
        # call run_operation to acquire it.
        self._edit_lock = RLock()
        
        # Track whether WASD keys should move the cursor (True) or camera (False)
        self._wasd_moves_cursor = False

    @property
    def wasd_moves_cursor(self) -> bool:
        """Whether WASD keys should move the cursor (True) or camera (False)."""
        return self._wasd_moves_cursor

    @wasd_moves_cursor.setter
    def wasd_moves_cursor(self, value: bool):
        """Set whether WASD keys should move the cursor (True) or camera (False)."""
        if self._wasd_moves_cursor != value:
            self._wasd_moves_cursor = value
            if self._file_panel is not None:
                self._file_panel.update_move_button()

    def _init_opengl(self):
        super()._init_opengl()
        self._file_panel = FilePanel(self)
        self._canvas_sizer.AddSpacer(30)
        self._tool_sizer = ToolManagerSizer(self)
        self._canvas_sizer.Add(self._tool_sizer, 1, wx.EXPAND, 0)

    def bind_events(self):
        """Set up all events required to run.
        Note this will also bind subclass events."""
        self._tool_sizer.bind_events()
        # binding the tool events first will run them last so they can't accidentally block UI events.
        super().bind_events()
        self._file_panel.bind_events()
        self.Bind(EVT_INPUT_PRESS, self._on_input_press)
        self.Bind(EVT_EDIT_CLOSE, self._on_close)

    def _on_input_press(self, evt: InputPressEvent):
        if (
            evt.action_id in SELECT_MODE_ACTIONS
            and not isinstance(self._tool_sizer._active_tool, SelectTool)
        ):
            wx.PostEvent(self, ToolChangeEvent(tool="Select"))
            if evt.action_id == ACT_INSPECT_POINT_1:
                wx.CallAfter(
                    lambda: wx.PostEvent(self, InputPressEvent(ACT_INSPECT_POINT_1))
                )

        if evt.action_id == ACT_HELP:
            webbrowser.open(
                "https://github.com/Amulet-Team/Amulet-Map-Editor/blob/master/amulet_map_editor/programs/edit/readme.md"
            )
        elif evt.action_id == ACT_PASTE:
            # If already in paste mode, paste from cache. Otherwise, switch to paste mode.
            if isinstance(self._tool_sizer._active_tool, PasteTool):
                self.paste_from_cache()
            else:
                wx.PostEvent(self, ToolChangeEvent(tool="Paste"))
        elif evt.action_id == ACT_SWITCH_TO_SELECT_MODE:
            wx.PostEvent(self, ToolChangeEvent(tool="Select"))
        elif evt.action_id == ACT_SWITCH_TO_PASTE_MODE:
            wx.PostEvent(self, ToolChangeEvent(tool="Paste"))
        elif evt.action_id == ACT_SWITCH_TO_FILL_MODE:
            wx.PostEvent(self, ToolChangeEvent(tool="Operation", state={"operation_name": "Fill"}))
        elif evt.action_id == ACT_SWITCH_TO_WATERLOG_MODE:
            wx.PostEvent(self, ToolChangeEvent(tool="Operation", state={"operation_name": "Waterlog"}))
        elif evt.action_id == ACT_SWITCH_TO_CLONE_MODE:
            wx.PostEvent(self, ToolChangeEvent(tool="Operation", state={"operation_name": "Clone"}))
        elif evt.action_id == ACT_SWITCH_TO_REPLACE_MODE:
            wx.PostEvent(self, ToolChangeEvent(tool="Operation", state={"operation_name": "Replace"}))
        elif evt.action_id == ACT_SWITCH_TO_BIOME_MODE:
            wx.PostEvent(self, ToolChangeEvent(tool="Operation", state={"operation_name": "Set Biome"}))
        elif evt.action_id == ACT_SWITCH_TO_IMPORT_MODE:
            wx.PostEvent(self, ToolChangeEvent(tool="Import"))
        elif evt.action_id == ACT_SWITCH_TO_EXPORT_MODE:
            wx.PostEvent(self, ToolChangeEvent(tool="Export"))
        elif evt.action_id == ACT_SWITCH_TO_CHUNK_MODE:
            wx.PostEvent(self, ToolChangeEvent(tool="Chunk"))
        elif evt.action_id == ACT_TOGGLE_FULLSCREEN:
            parent = self.GetTopLevelParent()
            if parent.IsFullScreen():
                parent.ShowFullScreen(False)
            else:
                parent.ShowFullScreen(True)
        elif evt.action_id == ACT_MOVE_CAMERA_TO_CURSOR:
            self._move_camera_to_selection_cursor()
        elif evt.action_id == ACT_TELEPORT_CURSOR_TO_CAMERA:
            self._teleport_selection_cursor_to_camera()
        elif evt.action_id == ACT_SAVE_ALL:
            self._save_all_worlds()
        elif evt.action_id == ACT_SAVE_ALL_CLOSE:
            self._save_all_worlds()
            close_level(self.world.level_path)
        elif evt.action_id == ACT_QUIT_WITHOUT_SAVE:
            top_level_parent = self.GetTopLevelParent()
            if top_level_parent is not None:
                if hasattr(top_level_parent, "force_quit_without_save"):
                    top_level_parent.force_quit_without_save()
                else:
                    top_level_parent.Destroy()
        evt.Skip()

    def _get_selection_center_and_size(self):
        selection_group = self.selection.selection_group
        if selection_group and selection_group.selection_boxes:
            min_x = min(box.min[0] for box in selection_group.selection_boxes)
            min_y = min(box.min[1] for box in selection_group.selection_boxes)
            min_z = min(box.min[2] for box in selection_group.selection_boxes)
            max_x = max(box.max[0] for box in selection_group.selection_boxes)
            max_y = max(box.max[1] for box in selection_group.selection_boxes)
            max_z = max(box.max[2] for box in selection_group.selection_boxes)
            center_x = (min_x + max_x) / 2
            center_y = (min_y + max_y) / 2
            center_z = (min_z + max_z) / 2
            size = (max_x - min_x, max_y - min_y, max_z - min_z)
            return (center_x, center_y, center_z), size
        return None, (0, 0, 0)

    def _move_camera_to_selection_cursor(self):
        target, size = self._get_selection_center_and_size()
        if target is None:
            return
        target_x, target_y, target_z = target

        yaw, pitch = self.camera.rotation
        yaw_radians = math.radians(yaw)
        pitch_radians = math.radians(pitch)

        forward_x = -math.sin(yaw_radians) * math.cos(pitch_radians)
        forward_y = -math.sin(pitch_radians)
        forward_z = math.cos(yaw_radians) * math.cos(pitch_radians)

        largest_axis = max(size)
        standoff_distance = max(8.0, largest_axis * 1.25)
        camera_x = target_x - forward_x * standoff_distance
        camera_y = target_y - forward_y * standoff_distance
        camera_z = target_z - forward_z * standoff_distance

        self.camera.location = (camera_x, camera_y, camera_z)

    def _teleport_selection_cursor_to_camera(self):
        selection_group = self.selection.selection_group
        camera_x, camera_y, camera_z = self.camera.location
        yaw, pitch = self.camera.rotation
        yaw_radians = math.radians(yaw)
        pitch_radians = math.radians(pitch)

        forward_x = math.cos(pitch_radians) * math.sin(yaw_radians)
        forward_y = -math.sin(pitch_radians)
        forward_z = math.cos(pitch_radians) * math.cos(yaw_radians)

        target_x = int(round(camera_x + forward_x * 5))
        target_y = int(round(camera_y + forward_y * 5 - 2))
        target_z = int(round(camera_z + forward_z * 5))

        if not selection_group or not selection_group.selection_boxes:
            self.selection.selection_corners = [
                ((target_x, target_y, target_z), (target_x + 1, target_y + 1, target_z + 1))
            ]
            return

        center, _ = self._get_selection_center_and_size()
        if center is None:
            return

        offset_x = target_x - int(round(center[0]))
        offset_y = target_y - int(round(center[1]))
        offset_z = target_z - int(round(center[2]))

        translated_corners = [
            (
                (box.min[0] + offset_x, box.min[1] + offset_y, box.min[2] + offset_z),
                (box.max[0] + offset_x, box.max[1] + offset_y, box.max[2] + offset_z),
            )
            for box in selection_group.selection_boxes
        ]
        self.selection.selection_corners = translated_corners

    def _save_all_worlds(self):
        """Save all open worlds in the notebook."""
        # Navigate up the widget hierarchy to find the notebook
        # EditCanvas -> EditExtension -> WorldPageUI -> AmuletLevelNotebook -> AmuletUI
        parent = self.GetParent()  # EditExtension
        if parent is None:
            return
        
        parent = parent.GetParent()  # WorldPageUI
        if parent is None:
            return
        
        parent = parent.GetParent()  # AmuletLevelNotebook
        if parent is None:
            return
        
        # Check if parent has _open_worlds attribute
        if not hasattr(parent, '_open_worlds'):
            return
        
        # Iterate through all open worlds and save their Edit extensions
        for path, world_page in parent._open_worlds.items():
            # world_page is a WorldPageUI; iterate through its extensions
            for page_index in range(world_page.GetPageCount()):
                extension = world_page.GetPage(page_index)
                # Check if this is an EditExtension with a canvas
                if hasattr(extension, '_canvas') and extension._canvas is not None:
                    extension._canvas.save()

    def enable(self):
        super().enable()
        self._tool_sizer.enable()
        self.PostSizeEvent()

    def disable(self):
        super().disable()
        self._tool_sizer.disable()

    def _on_close(self, _):
        close_level(self.world.level_path)

    @property
    def tools(self):
        return self._tool_sizer.tools

    @property
    def key_binds(self) -> KeybindGroup:
        config_ = CONFIG.get(EDIT_CONFIG_ID, {})
        keyboard_group = config_.get(
            "keyboard_keybind_group",
            config_.get("keybind_group", DefaultKeybindGroupId),
        )
        mouse_group = config_.get(
            "mouse_keybind_group",
            config_.get("keybind_group", DefaultKeybindGroupId),
        )

        user_keyboard_keybinds = config_.get(
            "user_keyboard_keybinds",
            {
                group_id: {
                    action: key
                    for action, key in group.items()
                    if action in KeyboardKeys
                }
                for group_id, group in config_.get("user_keybinds", {}).items()
            },
        )
        user_mouse_keybinds = config_.get(
            "user_mouse_keybinds",
            {
                group_id: {
                    action: key
                    for action, key in group.items()
                    if action in MouseKeys
                }
                for group_id, group in config_.get("user_keybinds", {}).items()
            },
        )

        keyboard_defaults = KeyboardPresets.get(keyboard_group, {})
        mouse_defaults = MousePresets.get(mouse_group, {})

        keyboard_keybinds = {
            **keyboard_defaults,
            **user_keyboard_keybinds.get(keyboard_group, {}),
        }
        mouse_keybinds = {
            **mouse_defaults,
            **user_mouse_keybinds.get(mouse_group, {}),
        }

        camera_look_bindings = {
            ACT_LOOK_UP: ((Alt,), W),
            ACT_LOOK_DOWN: ((Alt,), S),
            ACT_LOOK_LEFT: ((Alt,), A),
            ACT_LOOK_RIGHT: ((Alt,), D),
        }

        keyboard_keybinds.update(camera_look_bindings)

        return {**keyboard_keybinds, **mouse_keybinds}

    def _deselect(self):
        # TODO: Re-implement this
        self._tool_sizer.enable_default_tool()

    def run_operation(
        self,
        operation: OperationType,
        title="Amulet",
        msg="Running Operation",
        throw_exceptions=False,
    ) -> Any:
        try:
            out = self._run_operation(operation, title, msg, True)
        except BaseException as e:
            if throw_exceptions:
                raise e
        else:
            # If there were no errors create an undo point
            def create_undo():
                yield 0, "Creating Undo Point"
                yield from self.create_undo_point_iter()

            self._run_operation(create_undo, title, msg, False)

            return out

    def _run_operation(
        self,
        operation: OperationType,
        title: str,
        msg: str,
        cancelable: bool,
    ) -> Any:
        with self._edit_lock:
            if self._operation_running:
                raise Exception(
                    "run_operation cannot be called from within itself. "
                    "This function has already been called by parent code so you cannot run it again"
                )
            self._operation_running = True

            self.renderer.disable_threads()

            style = (
                wx.PD_APP_MODAL
                | wx.PD_ELAPSED_TIME
                | wx.PD_REMAINING_TIME
                | wx.PD_AUTO_HIDE
                | (wx.PD_CAN_ABORT * cancelable)
            )
            dialog = wx.ProgressDialog(
                title,
                msg,
                maximum=10_000,
                parent=self,
                style=style,
            )
            dialog.Fit()

            # Set up a thread to run the actual operation
            op = OperationThread(operation, msg)
            # run the operation
            op.start()
            while op.is_alive():
                op.join(0.1)
                dialog.Update(max(0, min(int(op.progress * 10_000), 9999)), op.message)
                wx.Yield()
                if dialog.WasCancelled():
                    op.stop = True

            dialog.Destroy()
            wx.Yield()

            if op.error is not None:
                # If there is any kind of error restore the last undo point
                self.world.restore_last_undo_point()

                if isinstance(op.error, BaseLoudException):
                    msg = str(op.error)
                    if isinstance(op.error, OperationError):
                        msg = f"Error running operation: {msg}"
                    log.info(msg)
                    wx.MessageDialog(self, msg, style=wx.OK).ShowModal()
                elif isinstance(op.error, BaseSilentException):
                    pass
                elif isinstance(op.error, BaseException):
                    tb = "".join(
                        traceback.format_exception(
                            type(op.error), op.error, op.error.__traceback__
                        )
                    )
                    log.error(tb)
                    dialog = TracebackDialog(
                        self,
                        "Exception while running operation",
                        str(op.error),
                        tb,
                    )
                    dialog.ShowModal()
                    dialog.Destroy()
                    self.world.restore_last_undo_point()

            self.renderer.enable_threads()
            self.renderer.render_world.rebuild_changed()
            self._operation_running = False
            if op.error is not None:
                raise op.error
            return op.out

    def create_undo_point(self, world=True, non_world=True):
        self.world.create_undo_point(world, non_world)
        wx.PostEvent(self, CreateUndoEvent())

    def create_undo_point_iter(
        self, world=True, non_world=True
    ) -> Generator[float, None, bool]:
        result = yield from self.world.create_undo_point_iter(world, non_world)
        wx.PostEvent(self, CreateUndoEvent())
        return result

    def undo(self):
        self.world.undo()
        self.renderer.render_world.rebuild_changed()
        wx.PostEvent(self, UndoEvent())

    def redo(self):
        self.world.redo()
        self.renderer.render_world.rebuild_changed()
        wx.PostEvent(self, RedoEvent())

    def cut(self):
        self.run_operation(
            lambda: cut(self.world, self.dimension, self.selection.selection_group)
        )

    def copy(self):
        self.run_operation(
            lambda: copy(self.world, self.dimension, self.selection.selection_group)
        )

    def paste(self, structure: BaseLevel, dimension: Dimension):
        assert isinstance(
            structure, BaseLevel
        ), "Structure given is not a subclass of BaseLevel."
        assert (
            dimension in structure.dimensions
        ), "The requested dimension does not exist for this object."
        wx.PostEvent(
            self,
            ToolChangeEvent(
                tool="Paste", state={"structure": structure, "dimension": dimension}
            ),
        )

    def paste_from_cache(self):
        if structure_cache:
            self.paste(*structure_cache.get_structure())
        else:
            wx.MessageBox("A structure needs to be copied before one can be pasted.")

    def delete(self):
        self.run_operation(
            lambda: delete(self.world, self.dimension, self.selection.selection_group)
        )

    def goto(self):
        location = show_goto(self, *self.camera.location)
        if location:
            self.camera.location = location

    def select_all(self):
        all_chunk_coords = tuple(self.world.all_chunk_coords(self.dimension))
        if all_chunk_coords:
            min_x, min_z = max_x, max_z = all_chunk_coords[0]
            for x, z in all_chunk_coords:
                if x < min_x:
                    min_x = x
                elif x > max_x:
                    max_x = x
                if z < min_z:
                    min_z = z
                elif z > max_z:
                    max_z = z

            self.selection.selection_corners = [
                (
                    (
                        min_x * self.world.sub_chunk_size,
                        self.world.bounds(self.dimension).min[1],
                        min_z * self.world.sub_chunk_size,
                    ),
                    (
                        (max_x + 1) * self.world.sub_chunk_size,
                        self.world.bounds(self.dimension).max[1],
                        (max_z + 1) * self.world.sub_chunk_size,
                    ),
                )
            ]

        else:
            self.selection.selection_corners = []

    def save(self):
        def pre_save() -> Generator[OperationYieldType, None, Any]:
            yield 0, "Running Pre-Save Operations."
            pre_save_op = self.world.pre_save_operation()
            try:
                while True:
                    yield next(pre_save_op)
            except StopIteration as e:
                if e.value:
                    yield from self.create_undo_point_iter()
                else:
                    self.world.restore_last_undo_point()

        def save() -> Generator[OperationYieldType, None, Any]:
            yield 0, "Saving Chunks."
            for chunk_index, chunk_count in self.world.save_iter():
                yield chunk_index / chunk_count

        self._run_operation(
            pre_save, "Running Pre-Save Operations.", "Please wait.", False
        )
        self._run_operation(save, "Saving world.", "Please wait.", False)
        wx.PostEvent(self, SaveEvent())
