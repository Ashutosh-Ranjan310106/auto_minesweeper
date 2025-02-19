import screen_area
import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab,Image
from time import sleep
#import pyttsx3
import pytesseract
#from pytesseract import image_to_string
from pynput.mouse import Controller,Button
from matplotlib import pyplot as plt
import pyperclip
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

mouse=Controller()




def find_img(template_path, screen, color, grid_size, char):
    print(template_path)
    template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    h, w = template.shape[:2]
    X, Y = cap.shape[:2]  
    cell_width, cell_height = X // grid_size[1], Y // grid_size[0]
    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)

    threshold = 0.8
    locations = np.where(result >= threshold)
    locations = list(zip(*locations[::-1]))

   # Filter out duplicate detections using non-maximum suppression
    filtered_locations = []
    for loc in locations:
        if all(abs(loc[0] - prev_loc[0]) > w // 2 or abs(loc[1] - prev_loc[1]) > h // 2 for prev_loc in filtered_locations):
            filtered_locations.append(loc)

    # Draw rectangles around filtered detected areas
    all_loc = filtered_locations[::]
    if filtered_locations:
        for loc in filtered_locations:
            top_left = loc
            bottom_right = (top_left[0] + w, top_left[1] + h)
            midle = (top_left[0] + w//2, top_left[1] + h//2)
            row, col = midle[1] // cell_height, midle[0] // cell_width
            if 0 <= row < grid_size[0] and 0 <= col < grid_size[1]:
                print(row,col)
                matrix[row][col] = char
            print(col)
            cv2.rectangle(screen, top_left, bottom_right, color, 2)
        print(f"Found {len(filtered_locations)} instances of the {template_path}")

    return all_loc




def find_number_in_box(locs, cap, grid_size, char):
    """Extract numbers and draw bounding boxes correctly."""
    X, Y = cap.shape[:2:]  
    cell_width, cell_height = X // grid_size[1], Y // grid_size[0]
    for loc in locs:
        top_left = loc
        

        # Adjust y-coordinates (Tesseract uses bottom-left origin)
        y1 = Y - top_left[1]
        x1 = top_left[0]

        # Compute grid position
        row, col = y1 // cell_height, x1 // cell_width

        # Validate if position is within bounds
        if 0 <= row < grid_size[0] and 0 <= col < grid_size[1]:
            print(row,col)
            matrix[col][row] = char
    return matrix




def make_matrix(screen, grid_size):

    p1 = "1.png", (0,255,0), 1
    p2 = "2.png", (0,0,255), 2
    p3 = "3.png", (144,144,144), 3
    p4 = "4.png", (10,10,10), 4
    p5 = "5.png", 5
    p6 = "6.png", 6
    flag = "flag.png", (255,0,0), -1

    all_img = [p1,p2, p3, p4, flag]
    for i in all_img:
        print(i)
        locs = find_img(i[0], screen, i[1], grid_size, i[2])
    return screen




def get_screen(cordinate):
    image=ImageGrab.grab(bbox=cordinate)
        # Convert to HSV color space
    image = np.array(image)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    
    # Apply Adaptive Thresholding for better OCR
    processed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                      cv2.THRESH_BINARY, 37, 16)


    return processed





def find_mine():
    pass
def do_chat_gpt(gpt_cordinate):
    pyautogui.click(gpt_cordinate[0], gpt_cordinate[1])
    pyperclip.copy(matrix)
    pyautogui.hotkey("ctrl", "v")  
    #pyautogui.press("enter")





def find_next_dig(matrix):
    height = len(matrix)
    width = len(matrix[0])

    safe_moves = []
    
    # Check every cell in the grid
    for row in range(height):
        for col in range(width):
            if matrix[row][col] > 0:  # If it's a number cell
                covered_neighbors = []
                mine_count = 0

                # Check surrounding 8 cells
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < height and 0 <= nc < width:
                            if matrix[nr][nc] == 0:  # Covered cell
                                covered_neighbors.append((nr, nc))
                            elif matrix[nr][nc] == -1:  # Flagged mine
                                mine_count += 1
                
                # If the number of flagged mines matches the number, dig remaining covered cells
                if mine_count == matrix[row][col]:
                    safe_moves.extend(covered_neighbors)

    return safe_moves  # Returns a list of (row, col) positions to dig next







print("scroll mouse to get screen cordinate")
a=0
if a:
    cordinate = screen_area.get_cordinate()
else:
    cordinate = [1104, 339, 1780, 865]    
print(cordinate)

print("scroll mouse to get gpt cordinate")
g=0
if g:
    gpt_cordinate = screen_area.get_cordinate()[:2:]
else:
    gpt_cordinate = [257, 854]
print(gpt_cordinate)

w,h = 18,14
matrix = [[0]*w for i in range(h) ]
while True:
    a=input("enter to next")
    cap = get_screen(cordinate)
    cap = make_matrix(cap, (w,h))
    cv2.imshow('Screen Capture', cap)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        for row in matrix:
            print(row)
       
        break
    print(find_next_dig(matrix))
    if False:
        
        break

#cv2.destroyAllWindows()



