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
from amulet_map_editor.api.wx.ui.simple import SimpleChoiceAny

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
    # Maps (tool_name, state_str) to (display_label, fkey)
    _mode_map: Dict[Tuple[str, Optional[str]], Tuple[str, str]] = {
        ("Select", None): ("F1 - Select", "Select:None"),
        ("Paste", None): ("F2 - Paste", "Paste:None"),
        ("Operation", "Fill"): ("F3 - Fill", "Operation:Fill"),
        ("Operation", "Waterlog"): ("F4 - Waterlog", "Operation:Waterlog"),
        ("Operation", "Clone"): ("F5 - Clone", "Operation:Clone"),
        ("Operation", "Replace"): ("F6 - Replace", "Operation:Replace"),
        ("Operation", "Set Biome"): ("F7 - Set Biome", "Operation:SetBiome"),
        ("Chunk", None): ("F8 - Chunk", "Chunk:None"),
        ("Export", None): ("F9 - Export", "Export:None"),
        ("Import", None): ("F10 - Import", "Import:None"),
    }

    def __init__(self, canvas: "EditCanvas"):
        wx.BoxSizer.__init__(self, wx.VERTICAL)
        EditCanvasContainer.__init__(self, canvas)

        self._tools: Dict[str, BaseToolUIType] = {}
        self._active_tool: Optional[BaseToolUIType] = None
        self._active_tool_state: Optional[Dict] = None

        self._tool_option_sizer = wx.BoxSizer(wx.VERTICAL)
        self.Add(
            self._tool_option_sizer, 1, wx.EXPAND | wx.RESERVE_SPACE_EVEN_IF_HIDDEN, 0
        )
        self.AddSpacer(30)

        self._tool_panel = wx.Panel(canvas.GetParent())
        self._tool_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self._tool_panel.SetSizer(self._tool_sizer)

        # Create mode selection dropdown
        self._mode_choice = SimpleChoiceAny(self._tool_panel, sort=False)
        self._tool_sizer.Add(self._mode_choice, 1, wx.EXPAND | wx.ALL, 5)
        self._mode_choice.Bind(wx.EVT_CHOICE, self._on_mode_choice)

        self.register_tool(SelectTool)
        self.register_tool(PasteTool)
        self.register_tool(OperationTool)
        self.register_tool(ImportTool)
        self.register_tool(ExportTool)
        self.register_tool(ChunkTool)

        self._populate_mode_choice()
        self._resize()

    def _populate_mode_choice(self):
        """Populate the choice dropdown with all available modes."""
        items = {}
        for (tool_name, state_name), (display_label, _) in self._mode_map.items():
            items[(tool_name, state_name)] = display_label
        self._mode_choice.SetItems(items)

    @property
    def tools(self):
        return self._tools.copy()

    def bind_events(self):
        if self._active_tool is not None:
            self._active_tool.bind_events()
        self.canvas.Bind(EVT_TOOL_CHANGE, self._enable_tool_event)
        self.canvas.Bind(wx.EVT_SIZE, self._on_resize)

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

    def _update_mode_choice_selection(self, tool_name: str, state: Optional[Dict]):
        """Update the dropdown to reflect the current tool/state."""
        state_name = None
        if state and "operation_name" in state:
            state_name = state["operation_name"]
        
        # Find the matching mode tuple in values
        target_tuple = (tool_name, state_name)
        if target_tuple in self._mode_choice.values:
            idx = self._mode_choice.values.index(target_tuple)
            self._mode_choice.SetSelection(idx)

    def _on_resize(self, evt) -> None:
        self._resize()
        evt.Skip()

    def _resize(self) -> None:
        window_size = self._tool_panel.GetBestSize()
        canvas_size = self.canvas.GetSize()
        self._tool_panel.SetSize(
            wx.Rect(
                max(0, canvas_size.GetWidth() // 2 - window_size.GetWidth() // 2),
                canvas_size.GetHeight() - window_size.GetHeight(),
                window_size.GetWidth(),
                window_size.GetHeight(),
            )
        )
        self._tool_panel.Raise()
        self._tool_panel.Refresh(False)
