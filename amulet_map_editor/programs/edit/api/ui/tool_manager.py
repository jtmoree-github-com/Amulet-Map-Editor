import wx
from typing import TYPE_CHECKING, Type, Dict, Optional, Tuple

from amulet_map_editor.programs.edit.api import EditCanvasContainer
from amulet_map_editor.programs.edit.api.ui.tool.base_tool_ui import (
    BaseToolUI,
    BaseToolUIType,
)
from amulet_map_editor.programs.edit.api.events import (
    ToolChangeEvent,
    EVT_TOOL_CHANGE,
)
from amulet_map_editor.api import lang

from amulet_map_editor.programs.edit.plugins.tools import (
    ImportTool,
    ExportTool,
    OperationTool,
    SelectTool,
    ChunkTool,
    PasteTool,
)

if TYPE_CHECKING:
    from amulet_map_editor.programs.edit.api.canvas import EditCanvas


class ToolManagerSizer(wx.BoxSizer, EditCanvasContainer):
    def __init__(self, canvas: "EditCanvas"):
        wx.BoxSizer.__init__(self, wx.VERTICAL)
        EditCanvasContainer.__init__(self, canvas)

        self._tools: Dict[str, BaseToolUIType] = {}
        self._active_tool: Optional[BaseToolUIType] = None
        self._active_tool_state: Optional[Dict] = None

        # Build mode map with translatable strings
        self._mode_map: Dict[Tuple[str, Optional[str]], Tuple[str, str]] = {
            ("Select", None): (f"F2 - {lang.get('mode.select')}", "Select:None"),
            ("Paste", None): (f"F3 - {lang.get('mode.paste')}", "Paste:None"),
            ("Operation", "Clone"): (f"F4 - {lang.get('mode.clone')}", "Operation:Clone"),
            ("Operation", "Replace"): (f"F5 - {lang.get('mode.replace')}", "Operation:Replace"),
            ("Operation", "Fill"): (f"F6 - {lang.get('mode.fill')}", "Operation:Fill"),
            ("Operation", "Waterlog"): (f"F7 - {lang.get('mode.waterlog')}", "Operation:Waterlog"),
            ("Operation", "Set Biome"): (f"F8 - {lang.get('mode.biome')}", "Operation:SetBiome"),
            ("Export", None): (f"F9 - {lang.get('mode.export')}", "Export:None"),
            ("Import", None): (f"F10 - {lang.get('mode.import')}", "Import:None"),
            ("Chunk", None): (f"F12 - {lang.get('mode.chunk')}", "Chunk:None"),
        }

        self._tool_option_sizer = wx.BoxSizer(wx.VERTICAL)
        self.Add(
            self._tool_option_sizer, 1, wx.EXPAND | wx.RESERVE_SPACE_EVEN_IF_HIDDEN, 0
        )
        self.AddSpacer(30)

        self.register_tool(SelectTool)
        self.register_tool(PasteTool)
        self.register_tool(OperationTool)
        self.register_tool(ImportTool)
        self.register_tool(ExportTool)
        self.register_tool(ChunkTool)

        self._populate_mode_choice()

    def _populate_mode_choice(self):
        """Populate the choice dropdown with all available modes."""
        items = {}
        for (tool_name, state_name), (display_label, _) in self._mode_map.items():
            items[(tool_name, state_name)] = display_label
        # Set items in the FilePanel's mode_choice
        if self.canvas._file_panel is not None:
            self.canvas._file_panel.set_mode_choice_items(items)

    @property
    def tools(self):
        return self._tools.copy()

    def bind_events(self):
        if self._active_tool is not None:
            self._active_tool.bind_events()
        self.canvas.Bind(EVT_TOOL_CHANGE, self._enable_tool_event)

    def register_tool(self, tool_cls: Type[BaseToolUIType]):
        assert issubclass(tool_cls, (wx.Window, wx.Sizer)) and issubclass(
            tool_cls, BaseToolUI
        )
        tool = tool_cls(self.canvas)
        tool_name = tool.name

        if isinstance(tool, wx.Window):
            tool.Hide()
        elif isinstance(tool, wx.Sizer):
            tool.ShowItems(show=False)
        self._tools[tool.name] = tool
        self._tool_option_sizer.Add(tool, 1, wx.EXPAND, 0)

    def _update_mode_choice_selection(self, tool_name: str, state: Optional[Dict]):
        """Update the dropdown to reflect the current tool/state."""
        state_name = None
        if state and "operation_name" in state:
            state_name = state["operation_name"]
        
        # Update selection in the FilePanel's mode_choice
        if self.canvas._file_panel is not None:
            self.canvas._file_panel.update_mode_choice_selection(tool_name, state_name)

    def _enable_tool_event(self, evt: ToolChangeEvent):
        self._enable_tool(evt.tool, evt.state)

    def enable(self):
        if isinstance(self._active_tool, SelectTool):
            self._active_tool.enable()
            self.canvas.reset_bound_events()
            self.canvas.Layout()
        else:
            self._enable_tool("Select")

    def disable(self):
        """Disable the active tool."""
        if self._active_tool is not None:
            self._active_tool.disable()

    def enable_default_tool(self):
        """
        Enables the default tool (the select tool)
        """
        if not isinstance(self._active_tool, SelectTool):
            self._enable_tool("Select")

    def _enable_tool(self, tool: str, state=None):
        if tool in self._tools:
            if self._active_tool is not None:
                if tool == "Paste" and isinstance(self._active_tool, PasteTool):
                    self._active_tool.confirm_paste()
                    return
                self._active_tool.disable()
                if isinstance(self._active_tool, wx.Window):
                    self._active_tool.Hide()
                elif isinstance(self._active_tool, wx.Sizer):
                    self._active_tool.ShowItems(show=False)
            self._active_tool = self._tools[tool]
            self._active_tool_state = state
            if isinstance(self._active_tool, wx.Window):
                self._active_tool.Show()
            elif isinstance(self._active_tool, wx.Sizer):
                self._active_tool.ShowItems(show=True)
            self._active_tool.enable()
            self._active_tool.set_state(state)
            
            # Update the dropdown selection
            self._update_mode_choice_selection(tool, state)
            
            self.canvas.reset_bound_events()
            self.canvas.Layout()

    def _current_mode_key(self):
        """Return the current (tool_name, state_name) key in _mode_map."""
        if self._active_tool is None:
            return None
        tool_name = self._active_tool.name
        state_name = None
        if self._active_tool_state and "operation_name" in self._active_tool_state:
            state_name = self._active_tool_state["operation_name"]
        key = (tool_name, state_name)
        if key in self._mode_map:
            return key
        return None

    def _cycle_mode(self, delta: int):
        """Cycle through the mode map by delta (+1 for next, -1 for prev)."""
        keys = list(self._mode_map.keys())
        if not keys:
            return
        current = self._current_mode_key()
        if current is not None and current in keys:
            idx = (keys.index(current) + delta) % len(keys)
        else:
            idx = 0
        tool_name, state_name = keys[idx]
        state = {"operation_name": state_name} if state_name else None
        wx.PostEvent(self.canvas, ToolChangeEvent(tool=tool_name, state=state))

    def next_mode(self):
        """Switch to the next mode in the hotbar."""
        self._cycle_mode(1)

    def prev_mode(self):
        """Switch to the previous mode in the hotbar."""
        self._cycle_mode(-1)
