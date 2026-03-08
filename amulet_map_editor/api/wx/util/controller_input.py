"""
Controller/Gamepad input handling for Amulet Map Editor.
Supports PlayStation, Xbox, and generic controllers via pygame.
"""

import wx
import logging
from typing import Dict, Set, Optional, Tuple, TYPE_CHECKING
import pygame

from .window_container import WindowContainer

if TYPE_CHECKING:
    from amulet_map_editor.programs.edit.api.key_config import KeybindGroup

log = logging.getLogger(__name__)

# Controller axis indices (common mapping)
AXIS_LEFT_STICK_X = 0
AXIS_LEFT_STICK_Y = 1
AXIS_RIGHT_STICK_X = 2
AXIS_RIGHT_STICK_Y = 3
AXIS_LEFT_TRIGGER = 4
AXIS_RIGHT_TRIGGER = 5

# PS4 button mapping (most common)
BTN_CROSS = 0      # X on Xbox
BTN_CIRCLE = 1     # B on Xbox
BTN_SQUARE = 2     # Y on Xbox
BTN_TRIANGLE = 3   # A on Xbox
BTN_L1 = 4
BTN_R1 = 5
BTN_L2 = 6
BTN_R2 = 7
BTN_SHARE = 8      # Back/Select on Xbox
BTN_OPTIONS = 9    # Start on Xbox
BTN_L3 = 10        # Left stick click
BTN_R3 = 11        # Right stick click
BTN_PS = 12        # Xbox button
BTN_TOUCHPAD = 13  # PS4 only

# Mapping from hardware button ID to controller button constant string
BUTTON_TO_STRING = {
    0: "CONTROLLER_CROSS",
    1: "CONTROLLER_CIRCLE",
    2: "CONTROLLER_SQUARE",
    3: "CONTROLLER_TRIANGLE",
    4: "CONTROLLER_SHARE",
    6: "CONTROLLER_OPTIONS",
    7: "CONTROLLER_L3",
    8: "CONTROLLER_R3",
    9: "CONTROLLER_L1",       # PS4 Left bumper
    10: "CONTROLLER_R1",      # PS4 Right bumper
    15: "CONTROLLER_TOUCHPAD",  # PS4 Touchpad
}

# D-pad mapping (from hat to button strings)
DPAD_TO_STRING = {
    (0, 1): "CONTROLLER_DPAD_UP",
    (0, -1): "CONTROLLER_DPAD_DOWN",
    (-1, 0): "CONTROLLER_DPAD_LEFT",
    (1, 0): "CONTROLLER_DPAD_RIGHT",
}

TRIGGER_PRESS_THRESHOLD = 0.5


class ControllerState:
    """Represents the current state of a controller."""
    
    def __init__(self):
        self.left_stick_x = 0.0
        self.left_stick_y = 0.0
        self.right_stick_x = 0.0
        self.right_stick_y = 0.0
        self.left_trigger = 0.0
        self.right_trigger = 0.0
        self.buttons_pressed: Set[int] = set()
        self.dpad_x = 0
        self.dpad_y = 0


class ControllerInput(WindowContainer):
    """A class to handle controller/gamepad input."""
    
    def __init__(self, window: wx.Window, deadzone: float = 0.15, sensitivity: float = 1.0):
        super().__init__(window)
        
        self._deadzone = deadzone
        self._sensitivity = sensitivity
        self._enabled = False
        
        # Initialize pygame joystick subsystem
        try:
            if not pygame.get_init():
                pygame.init()
            if not pygame.joystick.get_init():
                pygame.joystick.init()
        except Exception as e:
            log.error(f"Failed to initialize pygame for controller support: {e}")
            self._joystick = None
            return
        
        # Try to initialize the first controller
        self._joystick: Optional[pygame.joystick.Joystick] = None
        self._init_controller()
        
        self._state = ControllerState()
        self._previous_state = ControllerState()
        
        # Timer for polling controller state
        self._poll_timer = wx.Timer(self.window)
        
    def _init_controller(self):
        """Initialize the first available controller."""
        try:
            joystick_count = pygame.joystick.get_count()
            if joystick_count > 0:
                self._joystick = pygame.joystick.Joystick(0)
                self._joystick.init()
                log.info(f"Controller detected: {self._joystick.get_name()}")
                log.info(f"  Buttons: {self._joystick.get_numbuttons()}")
                log.info(f"  Axes: {self._joystick.get_numaxes()}")
            else:
                log.info("No controllers detected")
        except Exception as e:
            log.error(f"Failed to initialize controller: {e}")
            self._joystick = None
    
    def bind_events(self):
        """Set up all events required to run."""
        if self._joystick is None:
            return
        
        self.window.Bind(wx.EVT_TIMER, self._poll_controller, self._poll_timer)
        self.window.Bind(wx.EVT_WINDOW_DESTROY, self._on_destroy, self.window)
    
    def enable(self):
        """Start polling the controller."""
        if self._joystick is not None:
            self._enabled = True
            self._poll_timer.Start(16)  # ~60 FPS
    
    def disable(self):
        """Stop polling the controller."""
        self._enabled = False
        self._poll_timer.Stop()
    
    def _on_destroy(self, evt):
        """Clean up when window is destroyed."""
        self.disable()
        if self._joystick is not None:
            try:
                self._joystick.quit()
            except:
                pass
        evt.Skip()
    
    @property
    def is_available(self) -> bool:
        """Check if a controller is available."""
        return self._joystick is not None
    
    @property
    def controller_name(self) -> str:
        """Get the name of the connected controller."""
        if self._joystick is not None:
            return self._joystick.get_name()
        return "No Controller"
    
    def _apply_deadzone(self, value: float) -> float:
        """Apply deadzone to analog input."""
        if abs(value) < self._deadzone:
            return 0.0
        # Scale the remaining range
        sign = 1.0 if value > 0 else -1.0
        scaled = (abs(value) - self._deadzone) / (1.0 - self._deadzone)
        return sign * scaled * self._sensitivity

    def _map_button_id(self, button_id: int) -> Optional[str]:
        """Map a physical button ID to an internal controller key string."""
        if self._joystick is None:
            return None

        num_buttons = self._joystick.get_numbuttons()

        # Common XInput layout (10 buttons): L3/R3 are 8/9, triggers are axes.
        if num_buttons <= 10:
            xinput_map = {
                0: "CONTROLLER_CROSS",
                1: "CONTROLLER_CIRCLE",
                2: "CONTROLLER_SQUARE",
                3: "CONTROLLER_TRIANGLE",
                4: "CONTROLLER_L1",
                5: "CONTROLLER_R1",
                6: "CONTROLLER_SHARE",
                7: "CONTROLLER_OPTIONS",
                8: "CONTROLLER_L3",
                9: "CONTROLLER_R3",
            }
            return xinput_map.get(button_id)

        # Some DirectInput controllers expose D-pad as buttons 14-17.
        # PS4 on Windows reports D-pad as buttons 11-14.
        dpad_button_map = {
            11: "CONTROLLER_DPAD_UP",      # PS4 D-pad up
            12: "CONTROLLER_DPAD_DOWN",    # PS4 D-pad down
            13: "CONTROLLER_DPAD_LEFT",    # PS4 D-pad left
            14: "CONTROLLER_DPAD_RIGHT",   # PS4 D-pad right
            16: "CONTROLLER_DPAD_LEFT",    # DirectInput D-pad left (alt)
            17: "CONTROLLER_DPAD_RIGHT",   # DirectInput D-pad right (alt)
        }
        if button_id in dpad_button_map:
            return dpad_button_map[button_id]

        return BUTTON_TO_STRING.get(button_id)
    
    def _poll_controller(self, evt):
        """Poll the controller and update state."""
        if not self._enabled or self._joystick is None:
            return
        
        try:
            # Process pygame events (required for controller updates)
            pygame.event.pump()
            
            # Store previous state
            self._previous_state.left_stick_x = self._state.left_stick_x
            self._previous_state.left_stick_y = self._state.left_stick_y
            self._previous_state.right_stick_x = self._state.right_stick_x
            self._previous_state.right_stick_y = self._state.right_stick_y
            self._previous_state.left_trigger = self._state.left_trigger
            self._previous_state.right_trigger = self._state.right_trigger
            self._previous_state.buttons_pressed = self._state.buttons_pressed.copy()
            
            # Read analog sticks
            num_axes = self._joystick.get_numaxes()
            if num_axes >= 2:
                self._state.left_stick_x = self._apply_deadzone(self._joystick.get_axis(AXIS_LEFT_STICK_X))
                self._state.left_stick_y = self._apply_deadzone(self._joystick.get_axis(AXIS_LEFT_STICK_Y))
            if num_axes >= 4:
                self._state.right_stick_x = self._apply_deadzone(self._joystick.get_axis(AXIS_RIGHT_STICK_X))
                self._state.right_stick_y = self._apply_deadzone(self._joystick.get_axis(AXIS_RIGHT_STICK_Y))
            if num_axes >= 6:
                # Triggers often report -1 to 1, but we want 0 to 1
                lt = self._joystick.get_axis(AXIS_LEFT_TRIGGER)
                rt = self._joystick.get_axis(AXIS_RIGHT_TRIGGER)
                self._state.left_trigger = (lt + 1.0) / 2.0  # Convert -1..1 to 0..1
                self._state.right_trigger = (rt + 1.0) / 2.0
            
            # Read buttons
            self._state.buttons_pressed.clear()
            for i in range(self._joystick.get_numbuttons()):
                if self._joystick.get_button(i):
                    self._state.buttons_pressed.add(i)
            
            # Detect button press/release and post events
            # Buttons that were just pressed
            newly_pressed = self._state.buttons_pressed - self._previous_state.buttons_pressed
            if newly_pressed:
                log.debug(f"Controller hardware buttons pressed: {newly_pressed}")
            for button_id in newly_pressed:
                mapped_button = self._map_button_id(button_id)
                if mapped_button is not None:
                    self._post_button_event(mapped_button, pressed=True)
                else:
                    log.warning(f"Button {button_id} pressed but not in mapping")
            
            # Buttons that were just released
            newly_released = self._previous_state.buttons_pressed - self._state.buttons_pressed
            for button_id in newly_released:
                mapped_button = self._map_button_id(button_id)
                if mapped_button is not None:
                    self._post_button_event(mapped_button, pressed=False)

            # Emit virtual L2/R2 button events from trigger axes so triggers work
            # on controller layouts where they are not exposed as physical buttons.
            prev_lt_pressed = self._previous_state.left_trigger >= TRIGGER_PRESS_THRESHOLD
            prev_rt_pressed = self._previous_state.right_trigger >= TRIGGER_PRESS_THRESHOLD
            lt_pressed = self._state.left_trigger >= TRIGGER_PRESS_THRESHOLD
            rt_pressed = self._state.right_trigger >= TRIGGER_PRESS_THRESHOLD

            if lt_pressed and not prev_lt_pressed:
                self._post_button_event("CONTROLLER_L2", pressed=True)
            elif prev_lt_pressed and not lt_pressed:
                self._post_button_event("CONTROLLER_L2", pressed=False)

            if rt_pressed and not prev_rt_pressed:
                self._post_button_event("CONTROLLER_R2", pressed=True)
            elif prev_rt_pressed and not rt_pressed:
                self._post_button_event("CONTROLLER_R2", pressed=False)
            
            # Read D-pad (if available as hat)
            if self._joystick.get_numhats() > 0:
                hat = self._joystick.get_hat(0)
                prev_dpad = (self._previous_state.dpad_x, self._previous_state.dpad_y)
                self._state.dpad_x, self._state.dpad_y = hat
                
                # D-pad changed
                if hat != prev_dpad:
                    # Released previous direction
                    if prev_dpad in DPAD_TO_STRING:
                        button_released = DPAD_TO_STRING[prev_dpad]
                        self._post_button_event(button_released, pressed=False)
                    # Pressed new direction
                    if hat in DPAD_TO_STRING:
                        button_pressed = DPAD_TO_STRING[hat]
                        self._post_button_event(button_pressed, pressed=True)
            
        except Exception as e:
            log.error(f"Error polling controller: {e}")
    
    def _post_button_event(self, button_string: str, pressed: bool):
        """Dispatch a controller button press/release directly to ButtonInput."""
        try:
            buttons = getattr(self.window, 'buttons', None)
            if buttons is None:
                log.warning(f"Window {self.window} has no 'buttons' attribute")
                return
            
            if pressed:
                buttons.controller_press(button_string)
            else:
                buttons.controller_release(button_string)
        except Exception as e:
            log.error(f"Error dispatching controller button: {e}", exc_info=True)
    
    @property
    def left_stick(self) -> Tuple[float, float]:
        """Get left analog stick values (-1.0 to 1.0)."""
        return (self._state.left_stick_x, self._state.left_stick_y)
    
    @property
    def right_stick(self) -> Tuple[float, float]:
        """Get right analog stick values (-1.0 to 1.0)."""
        return (self._state.right_stick_x, self._state.right_stick_y)
    
    @property
    def left_trigger(self) -> float:
        """Get left trigger value (0.0 to 1.0)."""
        return self._state.left_trigger
    
    @property
    def right_trigger(self) -> float:
        """Get right trigger value (0.0 to 1.0)."""
        return self._state.right_trigger
    
    def is_button_pressed(self, button: int) -> bool:
        """Check if a button is currently pressed."""
        return button in self._state.buttons_pressed
    
    def was_button_just_pressed(self, button: int) -> bool:
        """Check if a button was just pressed this frame."""
        return (button in self._state.buttons_pressed and 
                button not in self._previous_state.buttons_pressed)
    
    def was_button_just_released(self, button: int) -> bool:
        """Check if a button was just released this frame."""
        return (button not in self._state.buttons_pressed and 
                button in self._previous_state.buttons_pressed)
    
    @property
    def any_input_active(self) -> bool:
        """Check if any input (stick, trigger, or button) is active."""
        return (abs(self._state.left_stick_x) > 0.01 or
                abs(self._state.left_stick_y) > 0.01 or
                abs(self._state.right_stick_x) > 0.01 or
                abs(self._state.right_stick_y) > 0.01 or
                self._state.left_trigger > 0.1 or
                self._state.right_trigger > 0.1 or
                len(self._state.buttons_pressed) > 0)
    
    @property
    def deadzone(self) -> float:
        """Get the current deadzone value."""
        return self._deadzone
    
    @deadzone.setter
    def deadzone(self, value: float):
        """Set the deadzone value (0.0 to 1.0)."""
        self._deadzone = max(0.0, min(1.0, value))
    
    @property
    def sensitivity(self) -> float:
        """Get the current sensitivity multiplier."""
        return self._sensitivity
    
    @sensitivity.setter
    def sensitivity(self, value: float):
        """Set the sensitivity multiplier."""
        self._sensitivity = max(0.1, min(5.0, value))
