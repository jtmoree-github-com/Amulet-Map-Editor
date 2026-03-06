from amulet_map_editor.api.opengl.data_types import RGBColour

from .colours import colours
from .render_selection import RenderSelection


class RenderSelectionPasteStatic(RenderSelection):
    @property
    def box_tint(self) -> RGBColour:
        return colours.get("box_clip_static", colours.get("box_paste_static", (0.72, 0.72, 0.72)))
