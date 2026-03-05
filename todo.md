# teminology

* Mouse Cursor
* Highlighter
* Preview/Caret/Shadow
* Clipboard

# todo

* conflicts with key appings in left mouse mode. 
* ctrl+shift+alt+D to toggle dimension?

## mouse toggles
* use Alt Mouse right for Camera toggle?
different hotkey for camera/cusor move toggle?
* use mouse button 3 for perspective toggle?
Ctrl+Mouse_right should toggle the move camera/move cursor

## misc
* inspect block with keyboard
* cursor /highlight speed not tied to camera speed.  maybe have a different speed cotnrol
* can we make the mode controls dockable so that they can open in a different window?

* ctrl+shift+alt+Q closes dialog boxes as well

## bugs
alt page up /down rotation
rotate automatically selects hightlight box?
* alt movements do not flip/rotate cursor with  wasd 


* There are no pneumonics on many menu entries.  suggest improvements
* fkeys do not work when keyboard focus is in a text field?
* research export interface.  it's confusing
* hot keys on save dialog disappeared?  every other load?
* make controls dialogs available on program open?
why does it ask to save when I have not changed anything?  is it recording camera postition?

# done

breaking changes are marked with !.  These are major departures from stock amulet.

## Selection and Highlighting
* B should set the target to point 1
* Shift B should start a box leaving the target wherever it is
* rename "Selection Box" => "Highlight Box"
* add another highlight box with keyboard only
* ! C to cycle through the highlight targets
* move multiselect from bottom of screen into nav bar like 2d/3d and move mouse/cursor
* ! default cursor position is next to camera.  click with mouse to move it
* ! place cursor on world load
* ! Change Alt for inspect block to require a mouse click
* any hotkey in select mode section activates select mode
* any hotkey in paste mode activates paste mode
* allow highlighting text in dialogs

## Hotkeys and Input
* hotkey for move camera to cursor to Shift+Ctrl+G
* map hotkey Alt+Ctrl+G to move cursor to camera
* map Ctrl+Q to Close World 
* ctrl+shift_Q to save all and close
* ctrl+alt+shift+Q to quit without saving
* Ctrl+Shift+S save all
* ctrl+R for run operation
* map Ctrl+F to search fields
* ! map keyboard keys for speed and zoom. consolidate keymaps
* alt for move to rotate cursor instead of camera
* ! Map backtick instead of TAB for perspective toggle.  
* ! dont map tab or shift for custom keys.  instead let them be normal
* Allow tab to move through dialogs
* fix interface tab navigation using Ctl+Page up/down and Shift+Ctrl+Page up/down
* fix tab does not go to the world list in the open dialog

## Controls and Keymap UI
* separate mouse mappings from keyboard mappings
* dont allow the keyboard mapping control window to map mouse actions
* require any mapping in the mouse control to include a mouse action
* remove buttons from un-editable control descriptions. only have keymap buttons for user defined mappings (groups)
* add controls and mouse dialog window management
* change labels on keymap groupings to right_hand_mouse, left_hand_mouse
* swap left/right on keys and control descriptions
* allow keyboard only paradigm
* BOX labels should use 'hightlight'

## Layout and Tabs
* put navigation buttons on top of 3d view as overlays allowing 3d view to be seen between controls (no separate bar)
* add "Convert World" title to Convert tab and make "Currently Opened World" a title on About tab
* remove Close world button from About and convert tabs in favor of the tab X and hotkeys
* add tooltip to X icon showing the hotkey
