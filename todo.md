# teminology

* Mouse Cursor (gray)
* Highlighter (multiple colors)
* Preview Caret (orange)
* Clipboard (white)

# todo

* add button to main menu named Backups.   It should open a new tab with controls for performaing backups.   There should be a text field and a file chooser to Choose the Folder where the backups will be written.  This should be saved and put back when the user re-opens amulet.  There should be a text field and folder chooser for where the minecraft worlds are stored and default to wherever they are.  A button named 'Backup Now' should be at the bottom.   When clicked it should backup everything in the worlds folder to a zip file in the backup folder.  the zip file should be named after the current date and time.   Default the backup folder to the user home folder.
* add delete button to main menu.  It should open a new tab.  On the tab it should list a text field and file chooser for where the minecraft worlds are stored.  should use the same location as the backups menu.
* in preferences dialog add a Button next to the Recent Worlds Limit on the right named "Clear" which deletes all of them.


Ctrl+A
Alt+A

* hotkey to start scaling operation?

## misc
* can we have a blender 3d keymap preset?
-- not really.   the workflows are too different.
* ctrl+shift+alt+D to toggle dimension?
* cursor /highlight speed not tied to camera speed.  maybe have a different speed cotnrol
* can we make the mode controls dockable so that they can open in a different window?
* research export interface.  it's confusing

## bugs
* There are no pneumonics on many menu entries.  suggest improvements
* fkeys do not work when keyboard focus is in a text field?
* hot keys on save dialog disappeared?  every other load?

# done

Breaking and significant changes are **bold**.  These are major departures from stock amulet.

* clarify terminology in interface
    - highlighter
    - mouse cursor
    - preview caret
    - clipboard (selection boxes)

## Selection and Highlighting
* **default cursor position is next to camera.  click with mouse to move it**
* **place cursor on world load**
* **Change Alt for inspect block to require a mouse click**
* **C to cycle through the highlight targets (formerly click and hold buttons)**
* paste caret (preview caret) now starts on top of clipboard instead of near camera
* fixed Alt rotation causing selection boxes to walk/drift along an axis
* move mode switching buttons from bottom of screen into nav bar like 2d/3d and move mouse/cursor
* map consistent colors to relate settings with 3d view targets
* inspect block with keyboard
* B should start highlight with expansion of point 1
* Shift B clear clipboard leaving the highlighter wherever it is
* add to clipboard with keyboard only
* any hotkey in select mode section activates select mode
* any hotkey in paste mode activates paste mode
* allow highlighting text in dialogs

## Hotkeys and Input
* **dont map tab or shift for custom keys.  instead let them be normal**
* **backtick instead of TAB for perspective toggle**  
* MIddle Mouse toggles the move camera/cursor
* configurable hotkey toggles camera/cusor
* Allow tab to move through dialogs
* Shift+Ctrl+G move camera to cursor
* Alt+Ctrl+G to move cursor to camera
* Ctrl+Q to Close World 
* ctrl+shift_Q to save all and close
* ctrl+alt+shift+Q to quit without saving
* ctrl+alt+shift+Q now closes all open dialogs (modal and modeless) before quitting
* Ctrl+Shift+S save all
* ctrl+R for run operation
* Ctrl+F to search fields
* keyboard keys for speed and zoom
* alt to rotate cursor instead of camera
* alt to rotate clipboard, preview caret
* Ctrl+P preferences dialog
* Ctrl+M Mouse Controls
* Ctrl+K Keyboard controls

## Controls and Keymap UI
* **consolidate keymaps**
* **change labels on keymap groupings to right_hand_mouse, left_hand_mouse**
* **separate mouse mappings from keyboard mappings**
* Alt Mouse Middle for perspective toggle
* dont allow the keyboard mapping control window to map mouse actions
* require any mapping in the mouse control to include a mouse action
* remove buttons from un-editable control descriptions. only have keymap buttons for user defined mappings (groups)
* swap left/right on keys and control descriptions
* allow keyboard only paradigm to move camera and selections
* add controls and mouse dialog window management

## Layout and Tabs
* fixed tab not displaying on program load
* fixed spurious "unsaved changes" prompt when closing world without making changes
* don't open new window for open world
* add "Convert World" title to Convert tab and make "Currently Opened World" a title on About tab
* remove Close world button from About and convert tabs in favor of the tab X and hotkeys
* add tooltip to X icon showing the hotkey
* fix interface tab navigation using Ctl+Page up/down and Shift+Ctrl+Page up/down
* fix tab does not go to the world list in the open dialog
* add friendly Bedrock world-lock handling with a clear “world database locked” warning instead of generic traceback flow
* improve Go To dialog usability by auto-focusing X on open and supporting Enter navigation x → y → z → OK
* update language strings for terminology consistency (Highlighter, selection/highlighter wording, new mouse action labels)
* Add menu and hotkey for 'Save As'
* support save as different format
* ctrl+Q and Esc cancel open world
* move MRU to main menu
* add MRU to file menu
