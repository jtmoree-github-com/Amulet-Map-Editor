# Amulet Map Editor - Feature Improvements Demo Script

## Overview
This script demonstrates the UI and UX improvements made to the Amulet Map Editor, including an integrated (keyboard-navigable) Open World dialog, mode selector consolidation, controls dialog improvements, and full keyboard-first accessibility. Total runtime: ~12–15 minutes.

---

## 1. Intro (0:00–0:30)

**Narration:**
"Hello, my name is JT. I will demonstrate improvements to the Amulet User Interface that focus on consolidating scattered controls, improving keyboard accessibility, clarifying configurable versus read-only settings.  This version of Amulet supports having both hands on the keyboard or one hand on the mouse.  My goal is to enable all functionality with either model."

**Action:**
- Open Amulet Map Editor

---

## 2. Open World Dialog Improvements (0:30–2:00)

**Narration:**
"First, we'll look at the Open World interface.  In stock Amulet, when we open a world, it pops up in a separate floating window only to be closed upon choosing an entry.  Now, it's integrated directly into the main application window as a tab so that all world related tabs are in one place.  There are still windows and dialogs that open like stock Amulet for modal funcationality that freezes the main window."

**Action:**
- Show mouse hover over Open World
- Use keyboard to move around main menu and spacebar to Activate Open World button
- Show the Open World dialog is now displayed as a built-in tab in the main interface
- Click on Main Menu tab and Choose Open World again

**Narration:**
"The most recent worlds are first to provide fast access to the last items worked on.  The full list of worlds are in an expanded tree view on the right.  We still have the two buttons for opening two different formats: directory and dot mcworld.  This page is fully navigable with the keyboard.  Tab moves between each component on the page.   Spacebar or Enter activates them."

**Action:**
- Demonstrate keyboard navigation in the Open World dialog:
  - Use Tab to move between fields/buttons
  - Use Arrow keys to navigate the world list
  - Use Enter to select/open a world
  - Show that the interface responds smoothly to keyboard input
- Keep hands off the mouse during this sequence to emphasize keyboard-only control

**Key Points:**
- Open World dialog now integrated as a tab (not a separate window)
- Full keyboard navigation support

---

## 3. Navigation UI Changes (2:00–3:00)

**Narration:**
"Amulet has different modes of operation. Features are different in Select mode than in Paste or Fill Operation. In stock Amulet, switching modes is done via buttons on the bottom of the screen. Since the modes are mutually exclusive and we want to know which one we are in, I moved this to a dropdown with the other navigation items on top.  It acts a label for the current mode."

**Action:**
- Load a world (if not already open)
- Hover over tabs to make them show up
- Point to the undo/redo/save buttons at top-left
- Point to the version info just below the toolbar buttons
- Highlight the mode selector dropdown showing: "Select, Paste, Clone, Replace, Fill, Waterlog, Set Biome, Export, Import, Chunk"
- Click the mode dropdown to show all modes available
- Click on a different mode to change it

**Narration:**
"This makes mode switching with the mouse slightly slower than the former dedicated buttons, but it puts navigation and context switching controls together. In addition, modes may be accessed via configurable hotkeys with F-keys mapped as the defaults."

**Action:**
- Press F12 to go into Chunk mode
- Press F6 to go into Fill mode

**Narration:**
"Next to the mode selector is the other navigation items like in stock Amulet. The perspective button, coordinates, move speed control, and dimension work the same as before. In addition to clicking the 2D/3D button, a hotkey of Ctrl+T switches perspective. This is a HUGE change from stock Amulet where the TAB key is very overloaded.  Using the tab key in that way makes moving around dialogs difficult.   We'll see that improvement later in this demo."

**Action:**
- Highlight other controls (location, speed, dimension)
- Click 2D/3D button
- Use Ctrl+T to get back to 3D mode

**Key Points:**
- Navigation controls grouped with related tools
- More viewport area visible
- More logical grouping with related controls
- Same F-key shortcuts still work (F2–F12)

---

## 4. Controls Dialog Improvements (3:00–4:30)

**Narration:**
"In addition to the mode switching hotkeys many more are available compared to stock Amulet.  You may view the hotkeys in the Controls editing screen where custom keymaps are defined.  The first hotkey I'll demo is the access of the keyboard controls.  Use Ctrl+K.  Note that I have a description of the control workflow in this version of Amulet since it departs from stock in some significant ways.   Some of the changes are backward compatible but a few are not such as the use of the Tab and Shift keys."

**Action:**
- Ctrl+K to bring up keyboard controls.

**Narration:**
"Next, notice that the default keymaps no longer have buttons for changing keymaps.  This is becuase those keymappings are not configurable.   The buttons worked as a shortcut to start a new keymap but I found that to be less helpful than confusing.  Instead all of the controls are listed here as read only text.  This is a one stop cheat sheet for controls.   All hotkeys are listed whether configurable or not.

**Action:**
- scroll down and up
- Choose right

**Narration:**
"When we want to create custom keymappings we use the stock Amulet feature of clicking the New button which is a green plus.  I map Help as Ctrl+H instead of the stock F1."

**Action:**
- click Add (green plus)
- name it test
- scroll down to modes
- remap help from F1 to Ctrl+H

**Narration:**
"Likewise, we may delete with the red minus and edit the group name with the edit icon.   You may notice that there are no mouse operations in this list.  I separated the mouse controls into a different dialog to reduce clutter.   Use Ctrl+M to open mouse settings.  The mouse and keyboard maps are still stored together using the same group name.   At some point it might make sense to completely separate them."

**Action:**
- Close dialog using OK button
- Ctrl+M
- Show group names including 'test'
- Close dialog

**Key Points:**
- F-keys organized numerically (F2–F12) for easy memorization
- Easy to rebind via controls dialog
- Consistent across all dialogs and dropdowns
- separate mouse and keyboard windows
- Reduced UI clutter in the controls dialog
- Clearer affordance for what can and can't be edited

---

## 5. Traditional Amulet Workflow (6:00–8:00)

**Narration:**
"Stock Amulet encourages us to keep one hand on the keyboard and one on the mouse.  This is similar to working in blender where the keyboard hand uses hot keys while the mouse hand pushes things around the interface."

**Action:**
- Go to Main Menu
- Click Open world
- Click on 3d tab
- Use Mode switcher to enter Select Mode
- Select some Blocks
- Copy Blocks with Copy button
- Use Mode Switcher to enter Paste Mode
- Move cursor with mouse
- Paste Blocks with Confirm

**Narration:**
"I added a hotkey of Ctrl+Shift+G that moves the camera to the cursor."

**Action:**
- Ctrl+Shift+G to jump camera to cursor location

**Narration:**
"In Stock Amulet there is a button to toggle the move keys from camera to cursor.  In this version of Amulet there is a button in the navigation bar to toggle the setting on and off.  This applies to almost all Modes.  copy, paste, chunk all use the same button."

**Action:**
- show Move Camera => Move Cursor button
- click button and move
- repeat to show difference

## 6. Keyboard-First Workflow (6:00–9:00)

**Narration:**
"Now we'll look at the workflow using only the keyboard. We'll start at the main menu and use Tab to move around, then Spacebar to open a world."

**Action:**
- Use keyboard only (no mouse):
  - Tab to move to Open World button and hit Spacebar
  - Tab to navigate to recent worlds list
  - Use Arrow keys to select a world
  - Press Enter to open the world

**Narration:**
To navigate the main window using only the keyboard. There are tabs on top which include the main menu and open worlds. Like with other programs we may use Ctrl+Page Up/Down to move around the main window tabs."

**Action:**
- Ctrl+Page Up to switch main tabs
- Open a second world from the main menu
- Ctrl+Page Down to show rotating between them.
- Leave it on one of the open worlds

**Narration:**
"Notice the tabs on the left which are related to the current world. To move between those tabs we may use Shift+Ctrl+Page Up/Down."

**Action:**
- Shift+Ctrl+Page. The 3D view will take a while
- Shift+Ctrl+Page Down

**Narration:**
"Once in the 3D view we may use the keyboard to move the camera as in stock Amulet but I have made a significant change. Stock Amulet uses the Minecraft key layout where Shift moves down and Spacebar moves up.  Since the Shift key is a modifier needed for other operations in Amulet I map UP to E and DOWN to X. This may take some getting used to. You can't see but I'm using E and X to move right now."

**Action:**
- Press F2 to switch to Select mode
- Use E, X to move up/down
- Move way up into the air
- Ctrl+Shift+G again

**Narration:**
"The cursor is highlighting just one block.  In this version of Amulet I use a hotkey of T to toggle the movement of camera or cursor."

**Action:**
- Move camera with WASD
- T to toggle
- Move cursor around with WASD

**Narration:**
"I have a departure from stock Amulet that could be added without breaking anything.  In this version I map the arrow keys and Page Up/Down to moving the cursor.  This allows us to move both the camera and cursor independently and at the same time with each hand."

**Action:**
- T to toggle back to camera mode
- Move camera with WASD while simultaneously moving cursor with Arrow keys
- Find something to copy such as a tree or patch of ground using the arrow keys and camera movement.

## 7. Selection Expansion with Keyboard (9:00–10:00)

**Narration:**
"Let's look at block highlighting. In Select mode, we have already seen how we can move the cursor for highlighting.  We can also expand the highlight box using keyboard controls.  Make sure we are in Select Mode with the F2 key.  We may use the arrow keys to move the box around or use the toggle for the other hand and use WASD, etc.  "

**Action:**
- F2
- Move box around using arrows

**Narration:**
"Next, I use the backtick key to switch to moving Point 1 only.  The same keys now move this point.  And backtick again to move Point 2.  backtick rotates between these three modes.  The mouse may also be used to click on these options in the dialog."

**Action:**
- Backtick
- Move boxes
- Backtick
- Move boxes
- Click with Mouse on Highlighter Text in Dialog

**Narration:**
"In stock Amulet, the TAB key was overloaded—it would switch between 2d/3d and perform some other tasks, making it difficult to navigate dialogs properly. In this version, TAB now works correctly for dialog navigation. Note that tab moves through the dialog controls.  If the keyboard focus is not on the dialog tab moves it there.   

**Action:**
- Tab through dialog

**Narration:**
"Now I'll show some hotkeys.  In the operations modes there are search fields.  Ctrl+F will put the keyboard focus on the search field and highlight the current text for easy replacement."

## 8. Paste Mode Keyboard Navigation (10:00–11:00)

**Narration:**
"I will demonstrate Paste mode with keyboard-only control. First, I'll copy some blocks in Select mode, then switch to Paste mode."

**Action:**
- Press F2 for Select mode
- Select a region of blocks
- Press Ctrl+C to copy
- Press Ctrl+V

**Narration:**
"When entering Paste mode, the structure to be pasted appears at the cursor location. In stock Amulet and in this one, there's an offset issue where the paste preview can appear far away on the Y axis, making it hard to find.   My goal with this version is to have the preview paste cursor appear on top of the highlight.  Then we can move it with keys or click with the mouse to move like in Stock Amulet."

**Action:**
- Show the paste preview appearing at the cursor location

**Narration:**
"I can move the paste preview using the same controls—WASD or arrow keys. The Paste operation panel has controls for rotation and flipping. Thanks to the TAB key fix, I can now navigate this dialog properly.  In addition, I can rotate and flip the cursor using Alt.  when moving the cursor with either WASD or Arrow Keys holding Alt with switch from moving to rotating and flipping. "

**Action:**
- Move the preview around using the keyboard
- Press Tab to navigate into the Paste controls panel
- Use Tab to move between rotation and flip buttons
- Press Spacebar or Enter to activate a rotation
- Show the paste preview rotating
- Tab to the flip control and activate it
- Show the paste preview flipping
- Use Arrow keys to fine-tune the paste position

**Narration:**
"Finally, I'll confirm the paste operation with Ctrl+V."

**Action:**
- Press Ctrl+V or Tab to the confirm button and press Enter
- Show the blocks being pasted
- Return to Select mode with F2

**Key Points:**
- Paste preview appears at cursor location (no offset issue)
- Full keyboard control for positioning
- TAB properly navigates the Paste controls panel
- Rotation and flip operations accessible via keyboard

---


## 9. Outro (11:00–11:30)

**Narration:**
"To summarize: we've restored navigation controls as overlays on the 3D view, moved the mode selector to a more prominent location, clarified which controls are editable and which are read-only, ensured new keybind groups inherit all settings, separated keyboard and mouse configuration dialogs, fixed the TAB key overload issue for proper dialog navigation, and smoothed out the overall editing experience. All of these changes aim to make Amulet faster and more intuitive to use, whether you prefer keyboard or mouse navigation."

**Action:**
- Return to main editor view with world loaded
- Pan camera while discussing navigation controls
- Final shot of the mode dropdown and navigation controls
- Fade out

---

---

# Shot-by-Shot Capture Checklist

Use this checklist to ensure you capture all necessary shots for the demo video. Check off each shot as you record.

## Section 1: Intro (0:00–0:30)

- [ ] **Shot 1a:** Amulet Map Editor title/splash screen
- [ ] **Shot 1b:** Full window view of main menu
- [ ] **Shot 1c:** Close-up or full window of main editor with loaded world

## Section 2: Open World Dialog Improvements (0:30–2:00)

- [ ] **Shot 2a:** Keyboard focus on Open World button, press Spacebar
- [ ] **Shot 2b:** Open World tab appears (integrated, not separate window)
- [ ] **Shot 2c:** Tab navigates to recent worlds list
- [ ] **Shot 2d:** Arrow keys navigate the world list
- [ ] **Shot 2e:** Press Enter to select and open a world
- [ ] **Shot 2f:** Click Main Menu tab
- [ ] **Shot 2g:** Click Open World again to show it can be reopened
- [ ] **Shot 2h:** Show full layout with recent worlds on left, tree view on right

## Section 3: Navigation UI Changes (2:00–3:00)

- [ ] **Shot 3a:** Full editor window showing loaded world with 3D view
- [ ] **Shot 3b:** Highlight undo/redo/save buttons at top-left
- [ ] **Shot 3c:** Highlight version info below toolbar buttons
- [ ] **Shot 3d:** Highlight top-right controls: 2D/3D, Move Camera/Cursor, Location, Speed, Dimension, Mode dropdown
- [ ] **Shot 3e:** Pan camera while discussing the navigation controls
- [ ] **Shot 3f:** Click mode dropdown to expand it, capturing all mode options
- [ ] **Shot 3g:** Click on a different mode (e.g., Fill) to show selection change
- [ ] **Shot 3h:** Press F12 to switch to Chunk mode
- [ ] **Shot 3i:** Press F6 to switch to Fill mode
- [ ] **Shot 3j:** Click 2D/3D button
- [ ] **Shot 3k:** Press Ctrl+T to toggle back to 3D mode

## Section 4: Controls Dialog Improvements (3:00–4:30)

- [ ] **Shot 4a:** Full editor window with Edit menu open
- [ ] **Shot 4b:** Click on "Controls" or "Keyboard Mapping" menu item
- [ ] **Shot 4c:** Controls dialog opens - wide shot showing full dialog
- [ ] **Shot 4d:** Scroll down to show "Default" preset displayed as bold text (no buttons)
- [ ] **Shot 4e:** Continue scrolling to show other read-only presets (multiple presets as bold text)
- [ ] **Shot 4f:** Scroll to find or show a custom user-defined group
- [ ] **Shot 4g:** Close-up of custom group showing buttons next to each key binding (editable)
- [ ] **Shot 4h:** Click "New Group" (or similar button) to create a new custom group
- [ ] **Shot 4i:** Dialog to name new group appears - type a name (e.g., "My Custom Controls")
- [ ] **Shot 4j:** Click OK or Confirm to create the group
- [ ] **Shot 4k:** New custom group now appears in list with editable buttons
- [ ] **Shot 4l:** Scroll within the dialog to show new group inherited keyboard AND mouse mappings

## Section 5: Hotkey Walkthrough (4:30–6:00)

- [ ] **Shot 5a:** Full view of Controls dialog showing keyboard section clearly
- [ ] **Shot 5b:** Close-up of F2 (Select) key binding in the list
- [ ] **Shot 5c:** Close-up of F3 (Paste) key binding
- [ ] **Shot 5d:** Scroll to show F4 (Clone) through F8 (Set Biome) bindings visible
- [ ] **Shot 5e:** Scroll to show F9 (Export), F10 (Import), and F12 (Chunk) bindings
- [ ] **Shot 5f:** Click one of the remap buttons to open key reassignment dialog
- [ ] **Shot 5g:** Key reassignment dialog is open (if separate window)
- [ ] **Shot 5h:** Press a different key to rebind (or click Cancel to close without change)
- [ ] **Shot 5i:** Return to main editor, mode dropdown visible at top
- [ ] **Shot 5j:** Click each mode in the dropdown to show F-key equivalents if listed (or just show selection changes)

## Section 6: Keyboard-First Workflow (6:00–9:00)

- [ ] **Shot 6a:** Main menu, Tab to Open World button, press Spacebar
- [ ] **Shot 6b:** Tab to recent worlds list, Arrow keys to select world
- [ ] **Shot 6c:** Press Enter to open world
- [ ] **Shot 6d:** World loads, show tabs at top
- [ ] **Shot 6e:** Press Ctrl+Page Up to switch main tabs
- [ ] **Shot 6f:** Press Ctrl+Page Down to cycle back
- [ ] **Shot 6g:** Open second world from main menu
- [ ] **Shot 6h:** Use Ctrl+Page Up/Down to show cycling between worlds
- [ ] **Shot 6i:** Press Shift+Ctrl+Page Up to show world tab switching
- [ ] **Shot 6j:** Press Shift+Ctrl+Page Down to go to 3D view
- [ ] **Shot 6k:** Press F2 for Select mode
- [ ] **Shot 6l:** Use E and X keys to move camera up/down (show movement)
- [ ] **Shot 6m:** Move up high into the air
- [ ] **Shot 6n:** Press Ctrl+Shift+G to jump to cursor
- [ ] **Shot 6o:** Use WASD to move camera
- [ ] **Shot 6p:** Press T to toggle cursor movement mode
- [ ] **Shot 6q:** Use WASD to move cursor instead of camera
- [ ] **Shot 6r:** Press T again to toggle back
- [ ] **Shot 6s:** Use WASD and Arrow keys simultaneously to move camera and cursor

## Section 7: Selection Expansion with Keyboard (9:00–10:00)

- [ ] **Shot 7a:** Press F2 to ensure in Select mode
- [ ] **Shot 7b:** Position cursor on a block and click to select
- [ ] **Shot 7c:** Press ` (backtick) to cycle selection box corner
- [ ] **Shot 7d:** Visual indicator shows active corner changing
- [ ] **Shot 7e:** Press Page Up to expand selection upward
- [ ] **Shot 7f:** Use Arrow keys (Right, Forward) to expand in those directions
- [ ] **Shot 7g:** Press ` again to change to different corner
- [ ] **Shot 7h:** Expand from new corner using arrow keys
- [ ] **Shot 7i:** Press F6 to open Fill mode dialog
- [ ] **Shot 7j:** Press Tab several times to navigate between controls
- [ ] **Shot 7k:** Use Arrow keys in dropdowns (if applicable)
- [ ] **Shot 7l:** Continue using Tab to navigate
- [ ] **Shot 7m:** Press Escape to close dialog

## Section 8: Paste Mode Keyboard Navigation (10:00–11:00)

- [ ] **Shot 8a:** Press F2 for Select mode
- [ ] **Shot 8b:** Select a region of blocks
- [ ] **Shot 8c:** Press Ctrl+C to copy
- [ ] **Shot 8d:** Press F3 to switch to Paste mode
- [ ] **Shot 8e:** Show paste preview appearing at cursor location
- [ ] **Shot 8f:** Use WASD and Arrow keys to position the preview
- [ ] **Shot 8g:** Press Tab to navigate into Paste controls panel
- [ ] **Shot 8h:** Tab to rotation button
- [ ] **Shot 8i:** Press Spacebar or Enter to rotate
- [ ] **Shot 8j:** Show paste preview rotating
- [ ] **Shot 8k:** Tab to flip control
- [ ] **Shot 8l:** Activate flip, show preview flipping
- [ ] **Shot 8m:** Use Arrow keys to fine-tune position
- [ ] **Shot 8n:** Press Ctrl+V or Tab to confirm button and press Enter
- [ ] **Shot 8o:** Show blocks being pasted
- [ ] **Shot 8p:** Press F2 to return to Select mode

## Section 9: Outro (11:00–11:30)

- [ ] **Shot 9a:** Full editor window with loaded world
- [ ] **Shot 9b:** Pan camera while discussing navigation controls
- [ ] **Shot 9c:** Wide shot of navigation controls
- [ ] **Shot 9d:** Close-up of mode dropdown showing final selection
- [ ] **Shot 9e:** Fade or transition to outro screen

---

## General Recording Tips

- **Audio:** Speak clearly into a good microphone; avoid background noise
- **Pacing:** Pause slightly between shots to allow narration to sync
- **Highlighting:** Use cursor circles or arrows in post-production to emphasize UI elements if needed
- **Transitions:** Quick cuts work well; fade to black between major sections is optional
- **Test shots:** Do a practice run to ensure all 10 modes appear correctly in the dropdown and dialogs load properly
- **Demo world:** Use a simple world to keep focus on the UI changes, not world details
- **Final check:** Verify all hotkeys (F2–F12) work as expected before recording

---

## Post-Production Checklist

- [ ] Audio levels normalized and background noise removed
- [ ] All shots in correct order per script
- [ ] Transitions smooth between sections
- [ ] On-screen graphics/text overlays added (if desired) for hotkey callouts
- [ ] Final video exports without codec errors
- [ ] Runtime approximately 12–15 minutes as expected
- [ ] Title card and outro credits (if applicable)
