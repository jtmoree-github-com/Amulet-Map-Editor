from amulet_map_editor.api.opengl.data_types import RGBColour

from .colours import colours
from .render_selection import RenderSelection


class RenderSelectionClipboard(RenderSelection):
    @property
    def box_tint(self) -> RGBColour:
        return colours.get("box_clip_static", colours.get("box_paste_static", (1.0, 1.0, 1.0)))
