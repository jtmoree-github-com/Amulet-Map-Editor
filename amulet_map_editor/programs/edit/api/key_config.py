from typing import List
from amulet_map_editor.api.wx.util.key_config import (
    KeybindContainer,
    KeybindGroup,
    KeybindGroupIdType,
    KeyActionType,
    Shift,
    MouseLeft,
    MouseMiddle,
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
    Return,
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
    F12,
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
P = "P"
Q = "Q"
R = "R"
B = "B"
F = "F"
C = "C"
G = "G"
Y = "Y"
H = "H"
U = "U"
M = "M"
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
ACT_LOOK_UP = "ACT_LOOK_UP"
ACT_LOOK_DOWN = "ACT_LOOK_DOWN"
ACT_LOOK_LEFT = "ACT_LOOK_LEFT"
ACT_LOOK_RIGHT = "ACT_LOOK_RIGHT"
ACT_ROTATE_CURSOR_UP = "ACT_ROTATE_CURSOR_UP"
ACT_ROTATE_CURSOR_DOWN = "ACT_ROTATE_CURSOR_DOWN"
ACT_ROTATE_CURSOR_LEFT = "ACT_ROTATE_CURSOR_LEFT"
ACT_ROTATE_CURSOR_RIGHT = "ACT_ROTATE_CURSOR_RIGHT"
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
ACT_TOGGLE_WASD_MODE_MOUSE = "ACT_TOGGLE_WASD_MODE_MOUSE"
ACT_BOX_CLICK = "ACT_BOX_CLICK"
ACT_BOX_CLICK_ADD = "ACT_BOX_CLICK_ADD"
ACT_BOX_CLICK_KEY = "ACT_BOX_CLICK_KEY"
ACT_CLEAR_START_HIGHLIGHT_BOX_ACTION = "ACT_CLEAR_START_HIGHLIGHT_BOX_ACTION"
ACT_BOX_CLICK_ADD_KEY = "ACT_BOX_CLICK_ADD_KEY"
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
ACT_INSPECT_POINT_1 = "ACT_INSPECT_POINT_1"
ACT_CHANGE_PROJECTION = "ACT_CHANGE_PROJECTION"
ACT_CHANGE_PROJECTION_MOUSE = "ACT_CHANGE_PROJECTION_MOUSE"
ACT_TOGGLE_FULLSCREEN = "ACT_TOGGLE_FULLSCREEN"
ACT_MOVE_CAMERA_TO_CURSOR = "ACT_MOVE_CAMERA_TO_CURSOR"
ACT_TELEPORT_CURSOR_TO_CAMERA = "ACT_TELEPORT_CURSOR_TO_CAMERA"
ACT_HELP = "ACT_HELP"
ACT_SAVE_ALL = "ACT_SAVE_ALL"
ACT_SAVE_ALL_CLOSE = "ACT_SAVE_ALL_CLOSE"
ACT_QUIT_WITHOUT_SAVE = "ACT_QUIT_WITHOUT_SAVE"

# Keyboard-only action keys (no mouse buttons/wheel)
KeyboardKeys: List[KeyActionType] = [
    ACT_MOVE_UP,
    ACT_MOVE_DOWN,
    ACT_MOVE_FORWARDS,
    ACT_MOVE_BACKWARDS,
    ACT_MOVE_LEFT,
    ACT_MOVE_RIGHT,
    ACT_LOOK_UP,
    ACT_LOOK_DOWN,
    ACT_LOOK_LEFT,
    ACT_LOOK_RIGHT,
    ACT_ROTATE_CURSOR_UP,
    ACT_ROTATE_CURSOR_DOWN,
    ACT_ROTATE_CURSOR_LEFT,
    ACT_ROTATE_CURSOR_RIGHT,
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
    ACT_BOX_CLICK_KEY,
    ACT_CLEAR_START_HIGHLIGHT_BOX_ACTION,
    ACT_BOX_CLICK_ADD_KEY,
    ACT_INCR_SPEED,
    ACT_DECR_SPEED,
    ACT_ZOOM_IN,
    ACT_ZOOM_OUT,
    ACT_INCR_SELECT_DISTANCE,
    ACT_DECR_SELECT_DISTANCE,
    ACT_DESELECT_ALL_BOXES,
    ACT_DESELECT_BOX,
    ACT_INSPECT_POINT_1,
    ACT_CHANGE_PROJECTION,
    ACT_TOGGLE_FULLSCREEN,
    ACT_MOVE_CAMERA_TO_CURSOR,
    ACT_TELEPORT_CURSOR_TO_CAMERA,
    ACT_HELP,
    ACT_SAVE_ALL,
    ACT_SAVE_ALL_CLOSE,
    ACT_QUIT_WITHOUT_SAVE,
]

# Mouse-related action keys
MouseKeys: List[KeyActionType] = [
    ACT_BOX_CLICK,
    ACT_BOX_CLICK_ADD,
    ACT_INSPECT_BLOCK,
    ACT_CHANGE_MOUSE_MODE,
    ACT_TOGGLE_WASD_MODE_MOUSE,
    ACT_CHANGE_PROJECTION_MOUSE,
    ACT_INCR_SPEED,
    ACT_DECR_SPEED,
    ACT_ZOOM_IN,
    ACT_ZOOM_OUT,
]

# Combined list for compatibility
KeybindKeys: List[KeyActionType] = KeyboardKeys + MouseKeys

PresetKeybinds: KeybindContainer = {
    "right": {
        ACT_MOVE_UP: ((), E),
        ACT_MOVE_DOWN: ((), X),
        ACT_MOVE_FORWARDS: ((), W),
        ACT_MOVE_BACKWARDS: ((), S),
        ACT_MOVE_LEFT: ((), A),
        ACT_MOVE_RIGHT: ((), D),
        ACT_LOOK_UP: ((Alt,), W),
        ACT_LOOK_DOWN: ((Alt,), S),
        ACT_LOOK_LEFT: ((Alt,), A),
        ACT_LOOK_RIGHT: ((Alt,), D),
        ACT_ROTATE_CURSOR_UP: ((Alt,), Up),
        ACT_ROTATE_CURSOR_DOWN: ((Alt,), Down),
        ACT_ROTATE_CURSOR_LEFT: ((Alt,), Left),
        ACT_ROTATE_CURSOR_RIGHT: ((Alt,), Right),
        ACT_CURSOR_UP: ((), PageUp),
        ACT_CURSOR_DOWN: ((), PageDown),
        ACT_CURSOR_FORWARDS: ((), Up),
        ACT_CURSOR_BACKWARDS: ((), Down),
        ACT_CURSOR_LEFT: ((), Left),
        ACT_CURSOR_RIGHT: ((), Right),
        ACT_PASTE: ((Control,), V),
        ACT_HELP: ((), F1),
        ACT_SWITCH_TO_SELECT_MODE: ((), F2),
        ACT_SWITCH_TO_PASTE_MODE: ((), F3),
        ACT_SWITCH_TO_CLONE_MODE: ((), F4),
        ACT_SWITCH_TO_REPLACE_MODE: ((), F5),
        ACT_SWITCH_TO_FILL_MODE: ((), F6),
        ACT_SWITCH_TO_WATERLOG_MODE: ((), F7),
        ACT_SWITCH_TO_BIOME_MODE: ((), F8),
        ACT_SWITCH_TO_EXPORT_MODE: ((), F9),
        ACT_SWITCH_TO_IMPORT_MODE: ((), F10),
        ACT_TOGGLE_FULLSCREEN: ((), F11),
        ACT_SWITCH_TO_CHUNK_MODE: ((), F12),
        ACT_SAVE_ALL: ((Control, Shift), S),
        ACT_SAVE_ALL_CLOSE: ((Control, Shift), Q),
        ACT_QUIT_WITHOUT_SAVE: ((Control, Alt, Shift), Q),
        ACT_TOGGLE_MOVE_TARGET: ((), C),
        ACT_TOGGLE_WASD_MODE: ((), T),
        ACT_CLEAR_START_HIGHLIGHT_BOX_ACTION: ((), B),
        ACT_BOX_CLICK_KEY: ((Shift,), B),
        ACT_BOX_CLICK_ADD_KEY: ((), V),
        ACT_BOX_CLICK: ((), MouseRight),
        ACT_BOX_CLICK_ADD: ((Control,), MouseRight),
        ACT_CHANGE_MOUSE_MODE: ((), MouseLeft),
        ACT_TOGGLE_WASD_MODE_MOUSE: ((Alt,), MouseLeft),
        ACT_INCR_SPEED: ((), MouseWheelScrollUp),
        ACT_DECR_SPEED: ((), MouseWheelScrollDown),
        ACT_ZOOM_IN: ((), MouseWheelScrollUp),
        ACT_ZOOM_OUT: ((), MouseWheelScrollDown),
        ACT_INCR_SELECT_DISTANCE: ((), R),
        ACT_DECR_SELECT_DISTANCE: ((), F),
        ACT_DESELECT_ALL_BOXES: ((Control, Shift), D),
        ACT_DESELECT_BOX: ((Control,), D),
        ACT_INSPECT_BLOCK: ((Alt,), MouseRight),
        ACT_CHANGE_PROJECTION_MOUSE: ((Control,), MouseLeft),
        ACT_INSPECT_POINT_1: ((), P),
        ACT_CHANGE_PROJECTION: ((), BACKTICK),
        ACT_MOVE_CAMERA_TO_CURSOR: ((Shift, Control), G),
        ACT_TELEPORT_CURSOR_TO_CAMERA: ((Alt, Control), G),
    },
    "left": {
        ACT_MOVE_UP: ((), U),
        ACT_MOVE_DOWN: ((), M),
        ACT_MOVE_FORWARDS: ((), I),
        ACT_MOVE_BACKWARDS: ((), K),
        ACT_MOVE_LEFT: ((), J),
        ACT_MOVE_RIGHT: ((), L),
        ACT_LOOK_UP: ((Alt,), I),
        ACT_LOOK_DOWN: ((Alt,), K),
        ACT_LOOK_LEFT: ((Alt,), J),
        ACT_LOOK_RIGHT: ((Alt,), L),
        ACT_ROTATE_CURSOR_UP: ((Alt,), Up),
        ACT_ROTATE_CURSOR_DOWN: ((Alt,), Down),
        ACT_ROTATE_CURSOR_LEFT: ((Alt,), Left),
        ACT_ROTATE_CURSOR_RIGHT: ((Alt,), Right),
        ACT_CURSOR_UP: ((), PageUp),
        ACT_CURSOR_DOWN: ((), PageDown),
        ACT_CURSOR_FORWARDS: ((), Up),
        ACT_CURSOR_BACKWARDS: ((), Down),
        ACT_CURSOR_LEFT: ((), Left),
        ACT_CURSOR_RIGHT: ((), Right),
        ACT_PASTE: ((Control,), V),
        ACT_HELP: ((), F1),
        ACT_SWITCH_TO_SELECT_MODE: ((), F2),
        ACT_SWITCH_TO_PASTE_MODE: ((), F3),
        ACT_SWITCH_TO_CLONE_MODE: ((), F4),
        ACT_SWITCH_TO_REPLACE_MODE: ((), F5),
        ACT_SWITCH_TO_FILL_MODE: ((), F6),
        ACT_SWITCH_TO_WATERLOG_MODE: ((), F7),
        ACT_SWITCH_TO_BIOME_MODE: ((), F8),
        ACT_SWITCH_TO_EXPORT_MODE: ((), F9),
        ACT_SWITCH_TO_IMPORT_MODE: ((), F10),
        ACT_TOGGLE_FULLSCREEN: ((), F11),
        ACT_SWITCH_TO_CHUNK_MODE: ((), F12),
        ACT_SAVE_ALL: ((Control, Shift), S),
        ACT_SAVE_ALL_CLOSE: ((Control, Shift), Q),
        ACT_QUIT_WITHOUT_SAVE: ((Control, Alt, Shift), Q),
        ACT_TOGGLE_MOVE_TARGET: ((), C),
        ACT_TOGGLE_WASD_MODE: ((), T),
        ACT_CLEAR_START_HIGHLIGHT_BOX_ACTION: ((), B),
        ACT_BOX_CLICK_KEY: ((Shift,), B),
        ACT_BOX_CLICK_ADD_KEY: ((), Return),
        ACT_BOX_CLICK: ((), MouseLeft),
        ACT_BOX_CLICK_ADD: ((Control,), MouseLeft),
        ACT_CHANGE_MOUSE_MODE: ((), MouseRight),
        ACT_TOGGLE_WASD_MODE_MOUSE: ((Alt,), MouseRight),
        ACT_INCR_SPEED: ((), MouseWheelScrollUp),
        ACT_DECR_SPEED: ((), MouseWheelScrollDown),
        ACT_ZOOM_IN: ((), MouseWheelScrollUp),
        ACT_ZOOM_OUT: ((), MouseWheelScrollDown),
        ACT_INCR_SELECT_DISTANCE: ((), R),
        ACT_DECR_SELECT_DISTANCE: ((), F),
        ACT_DESELECT_ALL_BOXES: ((Control, Shift), D),
        ACT_DESELECT_BOX: ((Control,), D),
        ACT_INSPECT_BLOCK: ((Alt,), MouseLeft),
        ACT_CHANGE_PROJECTION_MOUSE: ((Control,), MouseRight),
        ACT_INSPECT_POINT_1: ((), P),
        ACT_CHANGE_PROJECTION: ((), BACKTICK),
        ACT_MOVE_CAMERA_TO_CURSOR: ((Shift, Control), G),
        ACT_TELEPORT_CURSOR_TO_CAMERA: ((Alt, Control), G),
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
        ACT_TELEPORT_CURSOR_TO_CAMERA,
    ]),
    ("camera", [
        ACT_CHANGE_MOUSE_MODE,
        ACT_MOVE_UP,
        ACT_MOVE_DOWN,
        ACT_MOVE_FORWARDS,
        ACT_MOVE_BACKWARDS,
        ACT_MOVE_LEFT,
        ACT_MOVE_RIGHT,
        ACT_LOOK_UP,
        ACT_LOOK_DOWN,
        ACT_LOOK_LEFT,
        ACT_LOOK_RIGHT,
    ]),
    ("cursor", [
        ACT_CURSOR_UP,
        ACT_CURSOR_DOWN,
        ACT_CURSOR_FORWARDS,
        ACT_CURSOR_BACKWARDS,
        ACT_CURSOR_LEFT,
        ACT_CURSOR_RIGHT,
        ACT_ROTATE_CURSOR_UP,
        ACT_ROTATE_CURSOR_DOWN,
        ACT_ROTATE_CURSOR_LEFT,
        ACT_ROTATE_CURSOR_RIGHT,
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
        ACT_CLEAR_START_HIGHLIGHT_BOX_ACTION,
        ACT_BOX_CLICK_KEY,
        ACT_BOX_CLICK_ADD_KEY,
        ACT_BOX_CLICK,
        ACT_BOX_CLICK_ADD,
        ACT_TOGGLE_MOVE_TARGET,
        ACT_DESELECT_ALL_BOXES,
        ACT_DESELECT_BOX,
        ACT_INSPECT_BLOCK,
        ACT_INSPECT_POINT_1,
        ACT_INCR_SELECT_DISTANCE,
        ACT_DECR_SELECT_DISTANCE,
    ]),
    # ("paste_mode", []),
    # ("operation", []),
])

# Keyboard-only presets (excludes mouse bindings)
KeyboardPresets: KeybindContainer = {}
for preset_name, preset_bindings in PresetKeybinds.items():
    KeyboardPresets[preset_name] = {
        action: binding
        for action, binding in preset_bindings.items()
        if action in KeyboardKeys
    }
    # Add keyboard controls (period/comma) for both zoom and speed
    KeyboardPresets[preset_name][ACT_INCR_SPEED] = ((), DOT)
    KeyboardPresets[preset_name][ACT_DECR_SPEED] = ((), COMMA)
    KeyboardPresets[preset_name][ACT_ZOOM_IN] = ((), DOT)
    KeyboardPresets[preset_name][ACT_ZOOM_OUT] = ((), COMMA)

# Mouse-only presets
MousePresets: KeybindContainer = {}
for preset_name, preset_bindings in PresetKeybinds.items():
    MousePresets[preset_name] = {
        action: binding
        for action, binding in preset_bindings.items()
        if action in MouseKeys
    }

# Keyboard-only action groups
KeyboardActionGroups = OrderedDict([
    ("modes", [
        ACT_HELP,
        ACT_SWITCH_TO_SELECT_MODE,
        ACT_SWITCH_TO_PASTE_MODE,
        ACT_SWITCH_TO_CLONE_MODE,
        ACT_SWITCH_TO_REPLACE_MODE,
        ACT_SWITCH_TO_FILL_MODE,
        ACT_SWITCH_TO_WATERLOG_MODE,
        ACT_SWITCH_TO_BIOME_MODE,
        ACT_SWITCH_TO_EXPORT_MODE,
        ACT_SWITCH_TO_IMPORT_MODE,
        ACT_TOGGLE_FULLSCREEN,
        ACT_SWITCH_TO_CHUNK_MODE,
    ]),
    ("navigation", [
        ACT_CHANGE_PROJECTION,
        ACT_TOGGLE_WASD_MODE,
        ACT_MOVE_CAMERA_TO_CURSOR,
        ACT_TELEPORT_CURSOR_TO_CAMERA,
    ]),
    ("camera", [
        ACT_MOVE_UP,
        ACT_MOVE_DOWN,
        ACT_MOVE_FORWARDS,
        ACT_MOVE_BACKWARDS,
        ACT_MOVE_LEFT,
        ACT_MOVE_RIGHT,
        ACT_LOOK_UP,
        ACT_LOOK_DOWN,
        ACT_LOOK_LEFT,
        ACT_LOOK_RIGHT,
        ACT_ZOOM_IN,
        ACT_ZOOM_OUT,
        ACT_INCR_SPEED,
        ACT_DECR_SPEED,
    ]),
    ("cursor", [
        ACT_CURSOR_UP,
        ACT_CURSOR_DOWN,
        ACT_CURSOR_FORWARDS,
        ACT_CURSOR_BACKWARDS,
        ACT_CURSOR_LEFT,
        ACT_CURSOR_RIGHT,
        ACT_ROTATE_CURSOR_UP,
        ACT_ROTATE_CURSOR_DOWN,
        ACT_ROTATE_CURSOR_LEFT,
        ACT_ROTATE_CURSOR_RIGHT,
    ]),
    ("select_mode", [
        ACT_CLEAR_START_HIGHLIGHT_BOX_ACTION,
        ACT_BOX_CLICK_KEY,
        ACT_BOX_CLICK_ADD_KEY,
        ACT_INSPECT_POINT_1,
        ACT_TOGGLE_MOVE_TARGET,
        ACT_DESELECT_ALL_BOXES,
        ACT_DESELECT_BOX,
        ACT_INCR_SELECT_DISTANCE,
        ACT_DECR_SELECT_DISTANCE,
    ]),
])

# Mouse-only action groups
MouseActionGroups = OrderedDict([
    ("selection", [
        ACT_BOX_CLICK,
        ACT_BOX_CLICK_ADD,
        ACT_INSPECT_BLOCK,
    ]),
    ("camera", [
        ACT_CHANGE_MOUSE_MODE,
        ACT_TOGGLE_WASD_MODE_MOUSE,
        ACT_CHANGE_PROJECTION_MOUSE,
    ]),
    ("2d", [
        ACT_ZOOM_IN,
        ACT_ZOOM_OUT,
    ]),
    ("3d", [
        ACT_INCR_SPEED,
        ACT_DECR_SPEED,
    ]),
])