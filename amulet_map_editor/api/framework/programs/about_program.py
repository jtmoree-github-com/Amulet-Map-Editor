import wx
import webbrowser
from typing import TYPE_CHECKING

from amulet_map_editor.api import lang
from amulet_map_editor.api.wx.ui.simple import SimplePanel
from amulet_map_editor.api.datatypes import MenuData
from amulet_map_editor.api.framework.programs import BaseProgram

if TYPE_CHECKING:
    from amulet.api.level import BaseLevel


class AboutProgram(SimplePanel, BaseProgram):
    def __init__(self, container, world: "BaseLevel"):
        SimplePanel.__init__(self, container)
        self.world = world

        # Add title
        title = wx.StaticText(
            self,
            label=lang.get("program_about.currently_opened_world"),
        )
        font = title.GetFont()
        font.PointSize += 2
        font = font.Bold()
        title.SetFont(font)
        self.add_object(title, 0, wx.ALL | wx.CENTER)
        
        # Import here to avoid circular dependency
        from amulet_map_editor.api.wx.ui.select_world import WorldUI
        self.add_object(WorldUI(self, self.world.level_wrapper), 0, wx.ALL | wx.CENTER)
        self.add_object(
            wx.StaticText(
                self,
                label=f"{lang.get('program_about.choose_from_options')}\n<=================",
            ),
            0,
            wx.ALL | wx.CENTER,
        )

    def menu(self, menu: MenuData) -> MenuData:
        menu.setdefault(lang.get("menu_bar.options.menu_name"), {}).setdefault(
            "options", {}
        ).setdefault(
            f"{lang.get('program_3d_edit.menu_bar.file.preferences')}\tCtrl+P",
            lambda evt: self.GetTopLevelParent()._edit_preferences(),
        )
        menu.setdefault(lang.get("menu_bar.help.menu_name"), {}).setdefault(
            "help", {}
        ).setdefault(
            lang.get("program_3d_edit.menu_bar.help.user_guide"),
            lambda evt: self._help_controls(),
        )
        return menu

    @staticmethod
    def _help_controls():
        webbrowser.open(
            "https://github.com/Amulet-Team/Amulet-Map-Editor/blob/master/README.md"
        )
