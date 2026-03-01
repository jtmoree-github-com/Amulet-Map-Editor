from typing import List
from amulet_map_editor.api.wx.util.key_config import (
    KeybindContainer,
    KeybindGroup,
    KeybindGroupIdType,
    KeyActionType,
    Shift,
    MouseLeft,
    MouseRight,
    MouseWheelScrollUp,
    MouseWheelScrollDown,
    Control,
    Alt,
    Left,
    Right,
    Up,
    Down,
    PageUp,
    PageDown,
    Space,
    F1,
    F2,
    F3,
    F4,
    F5,
    F6,
    F7,
    F8,
    F9,
    F10,
    F11,
)

# Letter key constants for movement
W = "W"
E = "E"
S = "S"
A = "A"
D = "D"
T = "T"
X = "X"
I = "I"
K = "K"
J = "J"
L = "L"
V = "V"
Q = "Q"
R = "R"
B = "B"
F = "F"
C = "C"
Y = "Y"
H = "H"
# Special character keys
DOT = "."
COMMA = ","
SEMICOLON = ";"
BACKTICK = "`"
from collections import OrderedDict

ACT_MOVE_UP = "ACT_MOVE_UP"
ACT_MOVE_DOWN = "ACT_MOVE_DOWN"
ACT_MOVE_FORWARDS = "ACT_MOVE_FORWARDS"
ACT_MOVE_BACKWARDS = "ACT_MOVE_BACKWARDS"
ACT_MOVE_LEFT = "ACT_MOVE_LEFT"
ACT_MOVE_RIGHT = "ACT_MOVE_RIGHT"
ACT_CURSOR_UP = "ACT_CURSOR_UP"
ACT_CURSOR_DOWN = "ACT_CURSOR_DOWN"
ACT_CURSOR_FORWARDS = "ACT_CURSOR_FORWARDS"
ACT_CURSOR_BACKWARDS = "ACT_CURSOR_BACKWARDS"
ACT_CURSOR_LEFT = "ACT_CURSOR_LEFT"
ACT_CURSOR_RIGHT = "ACT_CURSOR_RIGHT"
ACT_PASTE = "ACT_PASTE"
ACT_SWITCH_TO_SELECT_MODE = "ACT_SWITCH_TO_SELECT_MODE"
ACT_SWITCH_TO_PASTE_MODE = "ACT_SWITCH_TO_PASTE_MODE"
ACT_SWITCH_TO_FILL_MODE = "ACT_SWITCH_TO_FILL_MODE"
ACT_SWITCH_TO_WATERLOG_MODE = "ACT_SWITCH_TO_WATERLOG_MODE"
ACT_SWITCH_TO_CLONE_MODE = "ACT_SWITCH_TO_CLONE_MODE"
ACT_SWITCH_TO_REPLACE_MODE = "ACT_SWITCH_TO_REPLACE_MODE"
ACT_SWITCH_TO_BIOME_MODE = "ACT_SWITCH_TO_BIOME_MODE"
ACT_SWITCH_TO_IMPORT_MODE = "ACT_SWITCH_TO_IMPORT_MODE"
ACT_SWITCH_TO_EXPORT_MODE = "ACT_SWITCH_TO_EXPORT_MODE"
ACT_SWITCH_TO_CHUNK_MODE = "ACT_SWITCH_TO_CHUNK_MODE"
ACT_TOGGLE_MOVE_TARGET = "ACT_TOGGLE_MOVE_TARGET"
ACT_FOCUS_PASTE_DIALOG = "ACT_FOCUS_PASTE_DIALOG"
ACT_TOGGLE_WASD_MODE = "ACT_TOGGLE_WASD_MODE"
ACT_BOX_CLICK = "ACT_BOX_CLICK"
ACT_BOX_CLICK_ADD = "ACT_BOX_CLICK_ADD"
ACT_CHANGE_MOUSE_MODE = "ACT_CHANGE_MOUSE_MODE"
ACT_INCR_SPEED = "ACT_INCR_SPEED"
ACT_DECR_SPEED = "ACT_DECR_SPEED"
ACT_ZOOM_IN = "ACT_ZOOM_IN"
ACT_ZOOM_OUT = "ACT_ZOOM_OUT"
ACT_INCR_SELECT_DISTANCE = "ACT_INCR_SELECT_DISTANCE"
ACT_DECR_SELECT_DISTANCE = "ACT_DECR_SELECT_DISTANCE"
ACT_DESELECT_ALL_BOXES = "ACT_DESELECT_ALL_BOXES"
ACT_DESELECT_BOX = "ACT_DESELECT_BOX"
ACT_INSPECT_BLOCK = "ACT_INSPECT_BLOCK"
ACT_CHANGE_PROJECTION = "ACT_CHANGE_PROJECTION"
ACT_TOGGLE_FULLSCREEN = "ACT_TOGGLE_FULLSCREEN"
ACT_MOVE_CAMERA_TO_CURSOR = "ACT_MOVE_CAMERA_TO_CURSOR"

KeybindKeys: List[KeyActionType] = [
    ACT_MOVE_UP,
    ACT_MOVE_DOWN,
    ACT_MOVE_FORWARDS,
    ACT_MOVE_BACKWARDS,
    ACT_MOVE_LEFT,
    ACT_MOVE_RIGHT,
    ACT_CURSOR_UP,
    ACT_CURSOR_DOWN,
    ACT_CURSOR_FORWARDS,
    ACT_CURSOR_BACKWARDS,
    ACT_CURSOR_LEFT,
    ACT_CURSOR_RIGHT,
    ACT_PASTE,
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
    ACT_TOGGLE_MOVE_TARGET,
    ACT_TOGGLE_WASD_MODE,
    ACT_BOX_CLICK,
    ACT_BOX_CLICK_ADD,
    ACT_CHANGE_MOUSE_MODE,
    ACT_INCR_SPEED,
    ACT_DECR_SPEED,
    ACT_ZOOM_IN,
    ACT_ZOOM_OUT,
    ACT_INCR_SELECT_DISTANCE,
    ACT_DECR_SELECT_DISTANCE,
    ACT_DESELECT_ALL_BOXES,
    ACT_DESELECT_BOX,
    ACT_INSPECT_BLOCK,
    ACT_CHANGE_PROJECTION,
    ACT_TOGGLE_FULLSCREEN,
    ACT_MOVE_CAMERA_TO_CURSOR,
]

PresetKeybinds: KeybindContainer = {
    "right": {
        ACT_MOVE_UP: ((), E),
        ACT_MOVE_DOWN: ((), X),
        ACT_MOVE_FORWARDS: ((), W),
        ACT_MOVE_BACKWARDS: ((), S),
        ACT_MOVE_LEFT: ((), A),
        ACT_MOVE_RIGHT: ((), D),
        ACT_CURSOR_UP: ((), PageUp),
        ACT_CURSOR_DOWN: ((), PageDown),
        ACT_CURSOR_FORWARDS: ((), Up),
        ACT_CURSOR_BACKWARDS: ((), Down),
        ACT_CURSOR_LEFT: ((), Left),
        ACT_CURSOR_RIGHT: ((), Right),
        ACT_PASTE: ((Control,), V),
        ACT_SWITCH_TO_SELECT_MODE: ((), F1),
        ACT_SWITCH_TO_PASTE_MODE: ((), F2),
        ACT_SWITCH_TO_FILL_MODE: ((), F3),
        ACT_SWITCH_TO_WATERLOG_MODE: ((), F4),
        ACT_SWITCH_TO_CLONE_MODE: ((), F5),
        ACT_SWITCH_TO_REPLACE_MODE: ((), F6),
        ACT_SWITCH_TO_BIOME_MODE: ((), F7),
        ACT_SWITCH_TO_IMPORT_MODE: ((), F10),
        ACT_SWITCH_TO_EXPORT_MODE: ((), F9),
        ACT_SWITCH_TO_CHUNK_MODE: ((), F8),
        ACT_TOGGLE_MOVE_TARGET: ((), BACKTICK),
        ACT_TOGGLE_WASD_MODE: ((Alt,), T),
        ACT_TOGGLE_FULLSCREEN: ((), F11),
        ACT_BOX_CLICK: ((), MouseLeft),
        ACT_BOX_CLICK_ADD: ((Control,), MouseLeft),
        ACT_CHANGE_MOUSE_MODE: ((), MouseRight),
        ACT_INCR_SPEED: ((), MouseWheelScrollUp),
        ACT_DECR_SPEED: ((), MouseWheelScrollDown),
        ACT_ZOOM_IN: ((), MouseWheelScrollUp),
        ACT_ZOOM_OUT: ((), MouseWheelScrollDown),
        ACT_INCR_SELECT_DISTANCE: ((), R),
        ACT_DECR_SELECT_DISTANCE: ((), F),
        ACT_DESELECT_ALL_BOXES: ((Control, Shift), D),
        ACT_DESELECT_BOX: ((Control,), D),
        ACT_INSPECT_BLOCK: ((Alt,), MouseRight),
        ACT_CHANGE_PROJECTION: ((Control,), T),
        ACT_MOVE_CAMERA_TO_CURSOR: ((Control,), Space),
    },
    "right_laptop": {
        ACT_MOVE_UP: ((), E),
        ACT_MOVE_DOWN: ((), X),
        ACT_MOVE_FORWARDS: ((), W),
        ACT_MOVE_BACKWARDS: ((), S),
        ACT_MOVE_LEFT: ((), A),
        ACT_MOVE_RIGHT: ((), D),
        ACT_CURSOR_UP: ((), PageUp),
        ACT_CURSOR_DOWN: ((), PageDown),
        ACT_CURSOR_FORWARDS: ((), Up),
        ACT_CURSOR_BACKWARDS: ((), Down),
        ACT_CURSOR_LEFT: ((), Left),
        ACT_CURSOR_RIGHT: ((), Right),
        ACT_PASTE: ((Control,), V),
        ACT_SWITCH_TO_SELECT_MODE: ((), F1),
        ACT_SWITCH_TO_PASTE_MODE: ((), F2),
        ACT_SWITCH_TO_FILL_MODE: ((), F3),
        ACT_SWITCH_TO_WATERLOG_MODE: ((), F4),
        ACT_SWITCH_TO_CLONE_MODE: ((), F5),
        ACT_SWITCH_TO_REPLACE_MODE: ((), F6),
        ACT_SWITCH_TO_BIOME_MODE: ((), F7),
        ACT_SWITCH_TO_IMPORT_MODE: ((), F10),
        ACT_SWITCH_TO_EXPORT_MODE: ((), F9),
        ACT_SWITCH_TO_CHUNK_MODE: ((), F8),
        ACT_TOGGLE_MOVE_TARGET: ((), BACKTICK),
        ACT_TOGGLE_WASD_MODE: ((Alt,), T),
        ACT_TOGGLE_FULLSCREEN: ((), F11),
        ACT_BOX_CLICK: ((), MouseLeft),
        ACT_BOX_CLICK_ADD: ((Control,), MouseLeft),
        ACT_CHANGE_MOUSE_MODE: ((), MouseRight),
        ACT_INCR_SPEED: ((), DOT),
        ACT_DECR_SPEED: ((), COMMA),
        ACT_ZOOM_IN: ((), DOT),
        ACT_ZOOM_OUT: ((), COMMA),
        ACT_INCR_SELECT_DISTANCE: ((), R),
        ACT_DECR_SELECT_DISTANCE: ((), F),
        ACT_DESELECT_ALL_BOXES: ((Control, Shift), D),
        ACT_DESELECT_BOX: ((Control,), D),
        ACT_INSPECT_BLOCK: ((Alt,), MouseRight),
        ACT_CHANGE_PROJECTION: ((Control,), T),
        ACT_MOVE_CAMERA_TO_CURSOR: ((Control,), Space),
    },
    "left": {
        ACT_MOVE_UP: ((), E),
        ACT_MOVE_DOWN: ((), X),
        ACT_MOVE_FORWARDS: ((), I),
        ACT_MOVE_BACKWARDS: ((), K),
        ACT_MOVE_LEFT: ((), J),
        ACT_MOVE_RIGHT: ((), L),
        ACT_CURSOR_UP: ((), PageUp),
        ACT_CURSOR_DOWN: ((), PageDown),
        ACT_CURSOR_FORWARDS: ((), Up),
        ACT_CURSOR_BACKWARDS: ((), Down),
        ACT_CURSOR_LEFT: ((), Left),
        ACT_CURSOR_RIGHT: ((), Right),
        ACT_PASTE: ((Control,), V),
        ACT_SWITCH_TO_SELECT_MODE: ((), F1),
        ACT_SWITCH_TO_PASTE_MODE: ((), F2),
        ACT_SWITCH_TO_FILL_MODE: ((), F3),
        ACT_SWITCH_TO_WATERLOG_MODE: ((), F4),
        ACT_SWITCH_TO_CLONE_MODE: ((), F5),
        ACT_SWITCH_TO_REPLACE_MODE: ((), F6),
        ACT_SWITCH_TO_BIOME_MODE: ((), F7),
        ACT_SWITCH_TO_IMPORT_MODE: ((), F10),
        ACT_SWITCH_TO_EXPORT_MODE: ((), F9),
        ACT_SWITCH_TO_CHUNK_MODE: ((), F8),
        ACT_TOGGLE_MOVE_TARGET: ((), BACKTICK),
        ACT_TOGGLE_WASD_MODE: ((Alt,), T),
        ACT_TOGGLE_FULLSCREEN: ((), F11),
        ACT_BOX_CLICK: ((), MouseLeft),
        ACT_BOX_CLICK_ADD: ((Control,), MouseLeft),
        ACT_CHANGE_MOUSE_MODE: ((), MouseRight),
        ACT_INCR_SPEED: ((), MouseWheelScrollUp),
        ACT_DECR_SPEED: ((), MouseWheelScrollDown),
        ACT_ZOOM_IN: ((), MouseWheelScrollUp),
        ACT_ZOOM_OUT: ((), MouseWheelScrollDown),
        ACT_INCR_SELECT_DISTANCE: ((), Y),
        ACT_DECR_SELECT_DISTANCE: ((), H),
        ACT_DESELECT_ALL_BOXES: ((Control, Shift), D),
        ACT_DESELECT_BOX: ((Control,), D),
        ACT_INSPECT_BLOCK: ((Alt,), MouseRight),
        ACT_CHANGE_PROJECTION: ((Control,), T),
        ACT_MOVE_CAMERA_TO_CURSOR: ((Control,), Space),
    },
    "left_laptop": {
        ACT_MOVE_UP: ((), E),
        ACT_MOVE_DOWN: ((), X),
        ACT_MOVE_FORWARDS: ((), I),
        ACT_MOVE_BACKWARDS: ((), K),
        ACT_MOVE_LEFT: ((), J),
        ACT_MOVE_RIGHT: ((), L),
        ACT_CURSOR_UP: ((), PageUp),
        ACT_CURSOR_DOWN: ((), PageDown),
        ACT_CURSOR_FORWARDS: ((), Up),
        ACT_CURSOR_BACKWARDS: ((), Down),
        ACT_CURSOR_LEFT: ((), Left),
        ACT_CURSOR_RIGHT: ((), Right),
        ACT_PASTE: ((Control,), V),
        ACT_SWITCH_TO_SELECT_MODE: ((), F1),
        ACT_SWITCH_TO_PASTE_MODE: ((), F2),
        ACT_SWITCH_TO_FILL_MODE: ((), F3),
        ACT_SWITCH_TO_WATERLOG_MODE: ((), F4),
        ACT_SWITCH_TO_CLONE_MODE: ((), F5),
        ACT_SWITCH_TO_REPLACE_MODE: ((), F6),
        ACT_SWITCH_TO_BIOME_MODE: ((), F7),
        ACT_SWITCH_TO_IMPORT_MODE: ((), F10),
        ACT_SWITCH_TO_EXPORT_MODE: ((), F9),
        ACT_SWITCH_TO_CHUNK_MODE: ((), F8),
        ACT_TOGGLE_MOVE_TARGET: ((), BACKTICK),
        ACT_TOGGLE_WASD_MODE: ((Alt,), T),
        ACT_TOGGLE_FULLSCREEN: ((), F11),
        ACT_BOX_CLICK: ((), MouseLeft),
        ACT_BOX_CLICK_ADD: ((Control,), MouseLeft),
        ACT_CHANGE_MOUSE_MODE: ((), MouseRight),
        ACT_INCR_SPEED: ((), DOT),
        ACT_DECR_SPEED: ((), COMMA),
        ACT_ZOOM_IN: ((), DOT),
        ACT_ZOOM_OUT: ((), COMMA),
        ACT_INCR_SELECT_DISTANCE: ((), Y),
        ACT_DECR_SELECT_DISTANCE: ((), H),
        ACT_DESELECT_ALL_BOXES: ((Control, Shift), D),
        ACT_DESELECT_BOX: ((Control,), D),
        ACT_INSPECT_BLOCK: ((Alt,), MouseRight),
        ACT_CHANGE_PROJECTION: ((Control,), T),
        ACT_MOVE_CAMERA_TO_CURSOR: ((Control,), Space),
    },
}

DefaultKeybindGroupId: KeybindGroupIdType = "right"
DefaultKeys: KeybindGroup = PresetKeybinds[DefaultKeybindGroupId]
# Action groupings for organized display
ActionGroups = OrderedDict([
    ("modes", [
        ACT_SWITCH_TO_SELECT_MODE,
        ACT_SWITCH_TO_PASTE_MODE,
        ACT_SWITCH_TO_FILL_MODE,
        ACT_SWITCH_TO_WATERLOG_MODE,
        ACT_SWITCH_TO_CLONE_MODE,
        ACT_SWITCH_TO_REPLACE_MODE,
        ACT_SWITCH_TO_BIOME_MODE,
        ACT_SWITCH_TO_CHUNK_MODE,
        ACT_SWITCH_TO_EXPORT_MODE,
        ACT_SWITCH_TO_IMPORT_MODE,
        ACT_TOGGLE_FULLSCREEN,
    ]),
    ("navigation", [
        ACT_CHANGE_PROJECTION,
        ACT_TOGGLE_WASD_MODE,
        ACT_MOVE_CAMERA_TO_CURSOR,
    ]),
    ("camera", [
        ACT_CHANGE_MOUSE_MODE,
        ACT_MOVE_UP,
        ACT_MOVE_DOWN,
        ACT_MOVE_FORWARDS,
        ACT_MOVE_BACKWARDS,
        ACT_MOVE_LEFT,
        ACT_MOVE_RIGHT,
    ]),
    ("cursor", [
        ACT_CURSOR_UP,
        ACT_CURSOR_DOWN,
        ACT_CURSOR_FORWARDS,
        ACT_CURSOR_BACKWARDS,
        ACT_CURSOR_LEFT,
        ACT_CURSOR_RIGHT,
    ]),
    ("2d", [
        ACT_ZOOM_IN,
        ACT_ZOOM_OUT,
    ]),
    ("3d", [
        ACT_INCR_SPEED,
        ACT_DECR_SPEED,
    ]),
    ("select_mode", [
        ACT_BOX_CLICK,
        ACT_BOX_CLICK_ADD,
        ACT_TOGGLE_MOVE_TARGET,
        ACT_DESELECT_ALL_BOXES,
        ACT_DESELECT_BOX,
        ACT_INSPECT_BLOCK,
        ACT_INCR_SELECT_DISTANCE,
        ACT_DECR_SELECT_DISTANCE,
    ]),
    # ("paste_mode", []),
    # ("operation", []),
])