import screen_area
import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab
from time import sleep
#import pyttsx3
import pytesseract
from pytesseract import image_to_string
from pynput.mouse import Controller,Button

import json
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
mouse=Controller()




def detect_numbers_by_blobs(screen, grid_size, matrix):

    _, binary = cv2.threshold(screen, 128, 255, cv2.THRESH_BINARY_INV)
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)

    Y, X = screen.shape[:2]
    cell_w, cell_h = X // grid_size[0], Y // grid_size[1]

    for i in range(1, num_labels):
        x, y, w, h, area = stats[i]
        cx, cy = centroids[i]
        col, row = int(cx // cell_w), int(cy // cell_h)
        if 0 <= row < grid_size[1] and 0 <= col < grid_size[0]:
            # Do OCR or template match just inside this small region
            roi = screen[y:y+h, x:x+w]
            text = image_to_string(roi, config='--psm 10 -c tessedit_char_whitelist=12345678')
            if text.strip().isdigit():
                matrix[row][col] = int(text.strip())
                cv2.rectangle(screen, (cell_w*col, cell_h*row), (cell_w*(col+1), cell_h*(row+1)), (0, 0, 255), 2)
    return matrix, screen



def load_colour_data(website_name, json_path="colour_data.json"):
    """
    Load color data for a specific website from a JSON file.
    The JSON should be structured as:
    {
        "website1": {
            "1": [R, G, B],
            "2": [R, G, B],
            ...
            "beige1": [R, G, B],
            ...
        },
        "website2": { ... }
    }
    """
    with open(json_path, "r") as f:
        all_data = json.load(f)
    if website_name not in all_data:
        raise ValueError(f"Website '{website_name}' not found in {json_path}")
    # Convert keys to int where possible, else keep as str
    site_data = {}
    for k, v in all_data[website_name].items():
        try:
            key = int(k)
        except ValueError:
            key = k
        site_data[key] = np.array(v)
    return site_data


def divide_and_highlight_nums(img, rows, cols):
    h, w, _ = img.shape
    cell_h, cell_w = h // rows, w // cols

    # Define green color range in HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    for i in range(rows):
        for j in range(cols):
            y1, y2 = i * cell_h+4, (i + 1) * cell_h-4
            x1, x2 = j * cell_w+4, (j + 1) * cell_w-4
            cell_hsv = hsv[y1:y2, x1:x2]
            found_color = None
            for name, bgr in colour_data.items():
                # Convert BGR to HSV for comparison
                hsv_color = cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)[0][0]
                lower = np.clip(hsv_color - np.array([10, 10, 10]), 0, 255)
                upper = np.clip(hsv_color + np.array([10, 10, 10]), 0, 255)
                mask = cv2.inRange(cell_hsv, lower, upper)
                if np.count_nonzero(mask) == mask.size:  # Only if the color fills the cell
                    found_color = name
                    break
                elif np.any(mask) and found_color is None:
                    found_color = name  # Mark if the color appears at least once

            if found_color:
                if found_color in ("beige1", "beige2"):
                    # For beige colors, use a different color for highlighting
                    color_bgr = [0, 0, 0]
                    matrix[i][j] = -2  # Mark as dug area
                    
                else:
                    color_bgr = colour_data[found_color].tolist()
                    try:
                        matrix[i][j] = int(found_color) 
                    except ValueError:
                        print(i,j, found_color)
                        raise SystemExit("Exiting as requested.")
                cv2.rectangle(img, (x1, y1), (x2, y2), color_bgr, 4)
                

    return img




def get_screen(cordinate):
    image=ImageGrab.grab(bbox=cordinate)
    image = np.array(image)
    return  image






def place_new_flag(matrix):
    rows, cols = len(matrix), len(matrix[0])
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    found=False
    probable_mines = {}
    for i in range(rows):
        for j in range(cols):
            if matrix[i][j] > 0:  # Dug cell with a number
                num_mines = matrix[i][j]
                flagged_count = 0
                undug_cells = []

                # Scan adjacent cells
                for dx, dy in directions:
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < rows and 0 <= nj < cols:
                        if matrix[ni][nj] == -1 or matrix[ni][nj] == -4:  # Already flagged
                            flagged_count += 1
                        elif matrix[ni][nj] == 0:  # Undug
                            undug_cells.append((ni, nj))

                # Only flag undug cells if exactly `num_mines - flagged_count` remain
                if  len(undug_cells) > 0:
                    if flagged_count + len(undug_cells) == num_mines:
                        for (fx, fy) in undug_cells:
                            matrix[fx][fy] = -4  # Place a new flag
                            found = True
                    elif flagged_count == num_mines:
                        for fx, fy in undug_cells:
                            matrix[fx][fy] = -3
                            found = True
                    elif not found:
                        probable_mines[(i,j)] = undug_cells


    if not found and probable_mines:
        for i in matrix:
            print(i)
        input('Press Enter to continue...')

        for (i, j), undug_cells in probable_mines.items():
            for fx, fy in undug_cells:
                matrix[fx][fy] = -1  # Tentatively flagging a mine
                flagged_count = 0
                temp_undug_cells = []

                # Count flags and gather undug cells around (i, j)
                for dx, dy in directions:
                    ni, nj = i + dx, j + dy
                    if 0 <= ni < rows and 0 <= nj < cols:
                        if matrix[ni][nj] == -1 or matrix[ni][nj] == -4:  # Already flagged
                            flagged_count += 1
                        elif matrix[ni][nj] == 0:  # Undug
                            temp_undug_cells.append((ni, nj))

                # If all required flags are placed, mark the rest as safe (-3)
                if flagged_count == matrix[i][j]:
                    for px, py in temp_undug_cells:
                        matrix[px][py] = -3  # Safe to dig
                else:
                    continue

                # Double-check surrounding flags for other probable mines
                for (ix, jx), other_undug_cells in probable_mines.items():
                    flagged_count = 0
                    undug_cells = []

                    # Scan adjacent cells
                    for dx, dy in directions:
                        ni, nj = ix + dx, jx + dy
                        if 0 <= ni < rows and 0 <= nj < cols:
                            if matrix[ni][nj] == -1 or matrix[ni][nj] == -4:  # Already flagged
                                flagged_count += 1
                            elif matrix[ni][nj] == 0:  # Undug
                                undug_cells.append((ni, nj))

                    # If flags + undug cells can't meet the requirement, unflag probable mine
                    if flagged_count + len(undug_cells) < matrix[ix][jx]:
                        print(f"Unflagging probable mine at: ({fx}, {fy})")
                        matrix[fx][fy] = -3  # Mark as likely safe
                        break
                else:
                    matrix[fx][fy] = 0  # Reset the flagged cell

                # Reset temporary undug cells
                for px, py in temp_undug_cells:
                    matrix[px][py] = 0

    
    return matrix, found






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
                    for r,c in covered_neighbors:
                        matrix[r][c] = -3
                    safe_moves.extend(covered_neighbors)
    return safe_moves, matrix  # Returns a list of (row, col) positions to dig next




def grafic_output(screen, grid_size, matrix):
    Y, X = screen.shape[:2]  
    cell_width, cell_height = X // grid_size[0], Y // grid_size[1]
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if matrix[i][j] == -3:
            # Safe to dig: Green
                cv2.drawMarker(screen, (j*cell_height + cell_height//2, i*cell_width + cell_width//2), color=(0, 255, 0), markerType=cv2.MARKER_STAR, thickness=2)
            elif matrix[i][j] == -4:
            # To be flagged: Red
                cv2.drawMarker(screen, (j*cell_height + cell_height//2, i*cell_width + cell_width//2), color=(0, 0, 255), markerType=cv2.MARKER_TILTED_CROSS, thickness=2)
    return screen

def place_flag(matrix, cordinate, grid_size):
    Y, X = image.shape[:2]  
    cell_width, cell_height = (X // grid_size[0]), (Y // grid_size[1])
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if matrix[i][j] == -4:
                #print(j*cell_height+ cell_height//2 + cordinate[1], i*cell_width + cell_width//2+cordinate[0], 'flag')
                pyautogui.click(j*cell_height+ cell_height//2+cordinate[0], i*cell_width + cell_width//2 + cordinate[1], button='right')
                matrix[i][j] = -1
    return matrix
def do_dig(matrix, cordinate, grid_size):
    Y, X = image.shape[:2]  
    cell_width, cell_height = (X // grid_size[0]), (Y // grid_size[1])
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if matrix[i][j] == -3:
                #print(j*cell_height+ cell_height//2 + cordinate[1], i*cell_width + cell_width//2+cordinate[0], 'dig')
                pyautogui.click(j*cell_height+ cell_height//2+cordinate[0], i*cell_width + cell_width//2 + cordinate[1], button='left')
    return matrix

print("scroll mouse to get screen cordinate")
a=1
if a:
    cordinate = screen_area.get_cordinate()
else:
    cordinate =   [953, 390, 1853, 870] # [1097, 356, 1781, 888]    #[1065, 310, 1816, 935]
print(cordinate)
cols, rows =  map(int,input('enter number of columns and rows format(c r):-').split()) #18,14 #10,8 #24,20
width = cordinate[2] - cordinate[0]
height = cordinate[3] - cordinate[1]

# Calculate the nearest greater width and height divisible by cols and rows
new_width = ((width) // cols) * cols
new_height = ((height) // rows) * rows

# Adjust the bottom-right coordinates
cordinate[2] = cordinate[0] + new_width
cordinate[3] = cordinate[1] + new_height

print(f"Adjusted Cordinate: {cordinate}")

website_name = "google_minesweeper"
colour_data = load_colour_data(website_name)
x=0
while True:
    x+=1
    #a=input("enter to next")
    matrix = [[0]*cols for i in range(rows) ]
    image = get_screen(cordinate)
    #cv2.imshow('gray Capture2', cap2)
    image = divide_and_highlight_nums(image, rows, cols)
    matrix, found = place_new_flag(matrix)
    out_image = grafic_output(image, (cols, rows), matrix)
    if x%5 == -1:
        sleep(5)
    if x%20 ==-1:
        input('Press Enter to continue...')
    cv2.imshow('gray Capture', out_image)
    #for row in matrix:
    #        print(row)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        for row in matrix:
            print(row)
        break
    #resize_ratio = 1
    matrix = place_flag(matrix, cordinate, (cols, rows))
    loc, matrix = find_next_dig(matrix)
    matrix = do_dig(matrix, cordinate, (cols, rows))

    sleep(0.5)

#cv2.destroyAllWindows()



