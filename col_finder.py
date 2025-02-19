import pyautogui
from PIL import ImageGrab
import time

def get_mouse_point_and_color():
    try:
        print("Move the mouse to the desired point and press Ctrl+C to capture...")
        while True:
            # Get the current mouse position
            x, y = pyautogui.position()
            
            # Capture the screen and get the color at the mouse position
            screen = ImageGrab.grab()
            color = screen.getpixel((x, y))
            
            # Display the coordinates and color
            print(f"Mouse Position: ({x}, {y}) | Color (RGB): {color}")
            
            # Wait for a short time to avoid spamming the console
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\nCapture complete!")

# Run the function
get_mouse_point_and_color()