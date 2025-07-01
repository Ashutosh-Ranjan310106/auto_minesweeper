import pyautogui
import tkinter as tk

def get_color_at_mouse():
    x, y = pyautogui.position()
    screenshot = pyautogui.screenshot()
    rgb = screenshot.getpixel((x, y))
    print(f"Mouse at ({x}, {y}) - RGB: {rgb}")

def on_key_press(event):
    get_color_at_mouse()

root = tk.Tk()
root.title("Color Picker")
root.geometry("300x100")
label = tk.Label(root, text="Move mouse and press SPACE to print RGB value", font=("Arial", 12))
label.pack(pady=20)
root.bind('<space>', on_key_press)
root.mainloop()