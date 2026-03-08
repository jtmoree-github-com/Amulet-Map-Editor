"""
Simple PS4 controller detection test
"""
import pygame

print("Initializing pygame...")
pygame.init()
pygame.joystick.init()

count = pygame.joystick.get_count()
print(f"\n{'='*60}")
print(f"Controllers detected: {count}")

if count > 0:
    for i in range(count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()
        print(f"\nController {i}:")
        print(f"  Name: {joystick.get_name()}")
        print(f"  Buttons: {joystick.get_numbuttons()}")
        print(f"  Axes: {joystick.get_numaxes()}")
        print(f"  Hats (D-pads): {joystick.get_numhats()}")
        print(f"  GUID: {joystick.get_guid()}")
    
    print(f"\n{'='*60}")
    print("SUCCESS! Controller detected.")
    print(f"{'='*60}")
    print("\nFor the full interactive test, run: python test_controller.py")
else:
    print(f"\n{'='*60}")
    print("NO CONTROLLERS FOUND")
    print(f"{'='*60}")
    print("\nTroubleshooting:")
    print("  1. Ensure PS4 controller is plugged in via USB")
    print("  2. Check if Windows recognizes it in:")
    print("     Settings > Devices > Bluetooth & other devices")
    print("  3. Try another USB port or cable")
    print("  4. Some PS4 controllers need DS4Windows driver installed")

pygame.quit()
