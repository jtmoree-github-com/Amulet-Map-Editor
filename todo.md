# teminology

* Mouse Cursor (gray)
* Highlighter (multiple colors)
* Preview Caret (orange)
* Clipboard (white)

# todo
* export/import interface?
* optimize gamepad controller mappings

## misc
* can we have a blender 3d keymap preset?
-- add G hotkey like blender that calls cut and paste
-- not completely.   the workflows are very different.
Ctrl+A yes
Alt+A  no already used...
shift+d (duplicate) => copy paste operation
* ctrl+shift+alt+D to toggle dimension?
* cursor /highlight speed not tied to camera speed.  maybe have a different speed cotnrol
* can we make the mode controls dockable so that they can open in a different window?
* hotkey to start scaling operation?

## bugs
* fkeys do not work when keyboard focus is in a text field?
* hot keys on save dialog disappeared?  every other load?

# done

Major changes that may not be liked by current userbase are **bold**.  Significant departures from stock amulet that are less invasive are *emphasized*.  Everything else can be ignored by users who don't want to use the new features.

* *clarify terminology in interface*
    - highlighter
    - mouse cursor
    - preview caret
    - clipboard (selection boxes)

## Layout and Tabs
* *refactor convert interface*
* update language strings for terminology consistency (Highlighter, selection/highlighter wording, new mouse action labels)
* fixed tabs not displaying on program load
* *rename Open World Button to => Worlds and menu File => Open World to Worlds*
* *move MRU to main menu*
* add MRU to file menu
* *change new window for open world into world managing tab in main window*
* Right click access to worlds in Worlds Menu.  e.g  Open, Save As, Delete
* cleaned up titles on World Tabs
* remove Close world button from About and convert tabs
* add tooltip to everything that displays all the time?
* fix main window tab navigation using Ctl+Page up/down
* fix world tab navigation using Shift+Ctrl+Page up/down
* add friendly Bedrock world-lock handling with a clear “world database locked” warning instead of generic traceback flow
* improve Go To dialog usability by auto-focusing X on open and supporting Enter navigation x → y → z → OK
* support save as different format from worlds and About Tab
* add Backups feature
* ctrl+Q and Esc cancel open world
* add pneumonics and clean up menus


## Selection and Highlighting
* **default cursor position is next to camera.  click with mouse to move it**
* **Change Alt for inspect block to require a mouse click**
* **C to cycle through the highlight targets (formerly click and hold buttons)**
* *move mode switching buttons from bottom of screen into nav bar like 2d/3d and move mouse/cursor*
* *place cursor on world load*
* *paste caret (preview caret) now starts on top of clipboard instead of near camera*
* all configuring of consistent colors to relate settings, dialogs, highlighter, etc.
* inspect block with keyboard
* B starts highlight with expansion of point 1
* Shift B clears clipboard leaving the highlighter wherever it is
* add to clipboard with keyboard only. equivalent to Ctrl Mouse click
* any hotkey in select mode section activates select mode
* any hotkey in paste mode activates paste mode
* allow highlighting text in dialogs

## Hotkeys and Input
* *dont map tab or shift for hotkeys.  let them act like other programs*
* Allow tab to move through dialogs and take focus to dialog when not there
* *backtick instead of TAB for perspective toggle*
* *configurable hotkey toggles camera/cusor* (formerly buttons)
* hotkey to move camera to cursor
* hotkey to move cursor to camera
* Ctrl+Q to Close World 
* ctrl+shift_Q to save all and close
* ctrl+alt+shift+Q to quit without saving
* Ctrl+Shift+A save all
* Ctrl+Shift+s save as (different name, different file format)
* ctrl+R for run operation
* Ctrl+F to search fields
* keyboard keys for speed and zoom
* alt to rotate camera
* alt to rotate clipboard, preview caret
* Ctrl+P preferences dialog
* Ctrl+M Mouse Controls
* Ctrl+K Keyboard controls

## Controls and Keymap UI
* *separate mouse mappings from keyboard mappings*
* *consolidate keymaps to left, right*
* **change labels on keymap groupings to right_hand_mouse, left_hand_mouse**
* **Change deselect all to Ctrl+Shift+A**
* dont allow the keyboard mapping control window to map mouse actions
* require any mapping in the mouse control to include a mouse action
* remove buttons from un-editable control descriptions. only have keymap buttons for user defined mappings (groups)
* swap left/right on keys and control descriptions
* allow keyboard only paradigm to move camera and selections
* add controls and mouse dialog window management from OS
* use modifiers with left and right mouse buttons for accessibility
* invert color on nav toggles
* add controller handler to use gamepads
