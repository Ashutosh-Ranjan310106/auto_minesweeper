from pynput.mouse import Controller as MouseController
from pynput.keyboard import Listener as KeyListener

mouse = MouseController()


def normalize_rect(p1, p2, p3, p4):
    left   = min(p1, p3)
    right  = max(p1, p3)
    top    = min(p2, p4)
    bottom = max(p2, p4)

    return [left, top, right, bottom]


def get_cordinate(cordinate_list):
    """
    Interactive coordinate adjustment.

    q → save current mouse position to index 0
    w → save current mouse position to index 1
    s → save and exit
    """

    # ensure list has 2 slots
    if len(cordinate_list) < 2:
        while len(cordinate_list) < 2:
            cordinate_list.append((0, 0))


    def on_press(key):

        try:
            k = key.char.lower()
        except AttributeError:
            return

        pos = list(mouse.position)

        if k == 'q':
            cordinate_list[0:2] = pos
            print("Point 0 set to:", pos)

        elif k == 'w':
            cordinate_list[2:4] = pos
            print("Point 1 set to:", pos)

        elif k == 's':
            print("Saved.")
            return False   # stop listener

    print("\nMove mouse → press Q / W to set points → press S to save\n")

    listener = KeyListener(on_press=on_press)
    listener.start()

    while listener.is_alive():
        listener.join(0.1)
    print(cordinate_list)
    rect = normalize_rect(*cordinate_list)
    cordinate_list[:] = rect
    return cordinate_list