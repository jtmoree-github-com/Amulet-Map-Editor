from amulet_map_editor.api.opengl.data_types import RGBColour

from .colours import colours
from .render_selection import RenderSelection


class RenderSelectionPointer(RenderSelection):
    @property
    def box_tint(self) -> RGBColour:
        return colours.get("box_pointer", colours.get("box_normal", (1, 1, 1)))
