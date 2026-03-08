"""
Test script to detect and display PS4 controller inputs.
Run this to verify your controller is working before implementing full support.

Requirements: pip install pygame
"""

import pygame
import sys
import time

def main():
    print("Initializing controller detection...")
    pygame.init()
    pygame.joystick.init()
    
    # Detect controllers
    joystick_count = pygame.joystick.get_count()
    print(f"\n{joystick_count} controller(s) detected")
    
    if joystick_count == 0:
        print("No controllers found. Please check:")
        print("  - Controller is plugged in via USB")
        print("  - Controller drivers are installed")
        print("  - Controller is powered on")
        return
    
    # Initialize first controller
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    
    print(f"\nController Info:")
    print(f"  Name: {joystick.get_name()}")
    print(f"  Buttons: {joystick.get_numbuttons()}")
    print(f"  Axes: {joystick.get_numaxes()}")
    print(f"  Hats: {joystick.get_numhats()}")
    
    print("\n" + "="*60)
    print("CONTROLLER TEST - Press Ctrl+C to exit")
    print("="*60)
    print("\nTry pressing buttons and moving sticks...")
    print("(Output updates when you interact with the controller)\n")
    
    clock = pygame.time.Clock()
    last_values = {}
    
    try:
        while True:
            pygame.event.pump()  # Process event queue
            
            current_values = {}
            changed = False
            
            # Read all buttons
            buttons = []
            for i in range(joystick.get_numbuttons()):
                if joystick.get_button(i):
                    buttons.append(i)
            if buttons:
                current_values['buttons'] = buttons
            
            # Read analog sticks and triggers
            axes = {}
            for i in range(joystick.get_numaxes()):
                value = joystick.get_axis(i)
                if abs(value) > 0.1:  # Deadzone
                    axes[i] = round(value, 2)
            if axes:
                current_values['axes'] = axes
            
            # Read D-pad (hat)
            for i in range(joystick.get_numhats()):
                hat = joystick.get_hat(i)
                if hat != (0, 0):
                    current_values['hat'] = hat
            
            # Check if anything changed
            if current_values != last_values:
                changed = True
                last_values = current_values.copy()
            
            if changed:
                # Clear previous output
                sys.stdout.write('\033[2J\033[H')  # Clear screen
                print("="*60)
                print("CONTROLLER INPUT (live)")
                print("="*60)
                
                if 'buttons' in current_values:
                    print(f"Buttons pressed: {current_values['buttons']}")
                    # PS4 button mapping (common)
                    button_names = {
                        0: "X (Cross)", 1: "O (Circle)", 2: "Square", 3: "Triangle",
                        4: "L1", 5: "R1", 6: "L2", 7: "R2",
                        8: "Share", 9: "Options", 10: "L3", 11: "R3",
                        12: "PS Button", 13: "Touchpad"
                    }
                    for btn in current_values['buttons']:
                        btn_name = button_names.get(btn, f"Button {btn}")
                        print(f"  - {btn_name}")
                
                if 'axes' in current_values:
                    print(f"\nAnalog Inputs:")
                    axis_names = {
                        0: "Left Stick X", 1: "Left Stick Y",
                        2: "Right Stick X", 3: "Right Stick Y",
                        4: "L2 Trigger", 5: "R2 Trigger"
                    }
                    for axis, value in current_values['axes'].items():
                        axis_name = axis_names.get(axis, f"Axis {axis}")
                        print(f"  {axis_name}: {value:+.2f}")
                
                if 'hat' in current_values:
                    hat_x, hat_y = current_values['hat']
                    directions = []
                    if hat_y == 1: directions.append("Up")
                    if hat_y == -1: directions.append("Down")
                    if hat_x == -1: directions.append("Left")
                    if hat_x == 1: directions.append("Right")
                    print(f"\nD-Pad: {' + '.join(directions)}")
                
                if not current_values:
                    print("(No input detected - controller idle)")
                
                print("\n" + "="*60)
            
            clock.tick(30)  # 30 FPS polling
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\n\nTest completed!")
        print("Controller is working correctly.")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
