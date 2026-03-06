from typing import Tuple
from amulet_map_editor.api.opengl.mesh.selection import (
    RenderSelection,
    RenderSelectionGroup,
)
from amulet_map_editor.api.opengl.mesh.selection.box.colours import colours


class GreenRenderSelection(RenderSelection):
    @property
    def box_tint(self) -> Tuple[float, float, float]:
        return colours.get("box_clipboard", (1.0, 0.7, 0.3))


class GreenRenderSelectionGroup(RenderSelectionGroup):
    def _new_render_selection(self):
        return GreenRenderSelection(self._context_identifier, self.resource_pack)
