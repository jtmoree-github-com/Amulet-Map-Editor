from typing import TYPE_CHECKING
import logging
import numpy

import wx
from wx.adv import RichToolTip
from amulet.api.chunk.biomes import BiomesShape

from .base_behaviour import BaseBehaviour
from .pointer_behaviour import PointerBehaviour
from ..events import (
    InputPressEvent,
    EVT_INPUT_PRESS,
)
from ..key_config import (
    ACT_INSPECT_BLOCK,
    ACT_INSPECT_POINT_1,
)

if TYPE_CHECKING:
    from ..canvas import EditCanvas

log = logging.getLogger(__name__)


class InspectBlockBehaviour(BaseBehaviour):
    """Adds a popup with block information."""

    def __init__(self, canvas: "EditCanvas", pointer_behaviour: PointerBehaviour):
        super().__init__(canvas)
        self._pointer_behaviour = pointer_behaviour

    def bind_events(self):
        """Set up all events required to run."""
        self.canvas.Bind(EVT_INPUT_PRESS, self._on_input_press)

    def _on_input_press(self, evt: InputPressEvent):
        """Logic to run each time the input press event is run."""
        if evt.action_id == ACT_INSPECT_BLOCK:
            self._inspect_block()
        elif evt.action_id == ACT_INSPECT_POINT_1:
            self._inspect_point_1()
        evt.Skip()

    def _inspect_block(self):
        x, y, z = self._pointer_behaviour.pointer_base
        self._inspect_at((x, y, z))

    def _inspect_point_1(self):
        if not hasattr(self._pointer_behaviour, "active_block_positions"):
            return
        if not getattr(self._pointer_behaviour, "selection_group", None):
            return

        point_1, _ = self._pointer_behaviour.active_block_positions
        self._inspect_at(point_1)

    def _inspect_at(self, location):
        def truncate(s: str, max_line_length: int = None) -> str:
            if isinstance(max_line_length, int):
                max_line_length = max(-1, max_line_length)
                s = "\n".join(
                    [
                        (
                            line[: max_line_length - 3] + "..."
                            if len(line) > max_line_length
                            else line
                        )
                        for line in s.split("\n")
                    ]
                )
            return s

        location = self._normalise_location(location)
        if location is None:
            return

        full_msg = self._get_block_info_message(location)
        msg = truncate(full_msg, 150)
        tooltip = RichToolTip("Inspect Block", msg)
        x, y = self._tooltip_anchor(location)
        tooltip.ShowFor(self.canvas, wx.Rect(x, y, 1, 1))

    def _normalise_location(self, location):
        try:
            if isinstance(location, (tuple, list)) and len(location) == 2:
                first = location[0]
                if isinstance(first, (tuple, list, numpy.ndarray)) and len(first) == 3:
                    location = first

            x, y, z = location
            return int(x), int(y), int(z)
        except Exception:
            log.error("Could not normalise inspect location: %r", location)
            return None

    def _tooltip_anchor(self, location):
        projected = self._project_world_to_screen(location)
        if projected is not None:
            return projected
        return self.canvas.mouse.xy

    def _project_world_to_screen(self, location):
        x, y, z = location
        width, height = self.canvas.GetSize()
        if width <= 0 or height <= 0:
            return None

        clip = numpy.matmul(
            self.canvas.camera.transformation_matrix,
            numpy.array((x + 0.5, y + 0.5, z + 0.5, 1.0)),
        )
        w = float(clip[3])
        if w == 0:
            return None

        ndc_x = float(clip[0]) / w
        ndc_y = float(clip[1]) / w
        if not (-1.0 <= ndc_x <= 1.0 and -1.0 <= ndc_y <= 1.0):
            return None

        sx = int((ndc_x + 1.0) * 0.5 * width)
        sy = int((1.0 - ndc_y) * 0.5 * height)
        return sx, sy

    def _get_block_info_message(self, location) -> str:
        x, y, z = location
        try:
            block = self.canvas.world.get_block(x, y, z, self.canvas.dimension)
            chunk = self.canvas.world.get_chunk(x >> 4, z >> 4, self.canvas.dimension)
            block_entity = chunk.block_entities.get((x, y, z), None)
            platform = self.canvas.world.level_wrapper.platform
            version = self.canvas.world.level_wrapper.version
            translator = self.canvas.world.translation_manager.get_version(
                platform,
                version,
            )
            (
                version_block,
                version_block_entity,
                _,
            ) = translator.block.from_universal(
                block, block_entity, block_location=(x, y, z)
            )
            if isinstance(version, tuple):
                version_str = ".".join(str(v) for v in version[:4])
            else:
                version_str = str(version)
            block_data_text = f"x: {x}, y: {y}, z: {z}\n\n{platform.capitalize()} {version_str}\n{version_block}"
            if version_block_entity:
                version_block_entity_str = str(version_block_entity)
                block_data_text = f"{block_data_text}\n{version_block_entity_str}"

            block_data_text = f"{block_data_text}\n\nUniversal\n{block}"
            if block_entity:
                block_entity_str = str(block_entity)
                block_data_text = f"{block_data_text}\n{block_entity_str}"

            if chunk.biomes.dimension == BiomesShape.Shape2D:
                biome = chunk.biomes[x % 16, z % 16]
                try:
                    block_data_text = f"{block_data_text}\n\nBiome: {self.canvas.world.biome_palette[biome]}"
                except Exception as e:
                    log.error(e)
            elif chunk.biomes.dimension == BiomesShape.Shape3D:
                biome = chunk.biomes[(x % 16) // 4, y // 4, (z % 16) // 4]
                try:
                    block_data_text = f"{block_data_text}\n\nBiome: {self.canvas.world.biome_palette[biome]}"
                except Exception as e:
                    log.error(e)

        except Exception as e:
            log.error(e)
            return str(e)
        else:
            return block_data_text
