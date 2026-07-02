import screen_area
import cv2
import numpy as np
import pyautogui
from PIL import ImageGrab
from pynput import keyboard
from time import sleep
#import pyttsx3
import statistics
import pytesseract
from pytesseract import image_to_string
from pynput.mouse import Controller,Button

import json
import argparse
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


def divide_and_highlight_nums(img, vlines, hlines, matrix):

    #h, w, _ = img.shape
    #cell_h = cell_w = cell_size

    # Define green color range in HSV    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    for i in range(len(hlines)-1):
        for j in range(len(vlines)-1):
            y1, y2 = hlines[i]+4, hlines[i+1]-4
            x1, x2 = vlines[j]+4, vlines[j+1]-4
            cell_hsv = hsv[y1:y2, x1:x2]
            found_color = None
            for name, bgr in colour_data.items():
                # Convert BGR to HSV for comparison
                hsv_color = cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)[0][0]
                lower = np.clip(hsv_color - np.array([5, 5, 5]), 0, 255)
                upper = np.clip(hsv_color + np.array([5, 5, 5]), 0, 255)
                try:
                    mask = cv2.inRange(cell_hsv, lower, upper)
                except:
                    print(x1,x2,y1,y2, cell_hsv.shape)
                if np.count_nonzero(mask) == mask.size:  # Only if the color fills the cell
                    found_color = name
                    break
                elif np.any(mask) and found_color is None:
                    found_color = name  # Mark if the color appears at least once

            if found_color:
                if found_color in ("beige1", "beige2"):
                    # For beige colors, use a different color for highlighting
                    color_bgr = [0, 0, 0]
                    try:
                        matrix[i][j] = -2  # Mark as dug area
                    except:
                        print(i,j)
                    #continue
                    
                else:
                    color_bgr = colour_data[found_color].tolist()
                    matrix[i][j] = int(found_color) 
                cv2.rectangle(img, (x1-2, y1-2), (x2-2, y2-2), color_bgr, 2)
    return img




def get_screen(cordinate):
    image=ImageGrab.grab(bbox=cordinate)
    image = np.array(image)
    return  image


def cluster_sorted(arr, max_gap):
    if not arr:
        return []

    clusters = [[arr[0]]]

    for i in range(1, len(arr)):
        if arr[i] - arr[i-1] <= max_gap:
            clusters[-1].append(arr[i])
        else:
            clusters.append([arr[i]])
    for i in range(len(clusters)):
        clusters[i] = round(statistics.median(clusters[i]))
    return clusters
def get_lines(img):
    output = img
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 0, 10)
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi/180,
        threshold=10,
        minLineLength=25,
    )
    vertical_lines = []
    if lines is not None: 
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(x1 - x2) < 5:   # nearly vertical
                vertical_lines.append(x1)
    vertical_lines = sorted(vertical_lines)
    vertical_lines = cluster_sorted(vertical_lines, max_gap=10)
    vertical_mode_lines = []
    distances = []
    for i in range(len(vertical_lines) - 1):
        d = vertical_lines[i+1] - vertical_lines[i]
        if d > 10:  # ignore duplicates
            distances.append(d)    
    try:
        vcell_size = int(statistics.mode(distances))
    except:
        return -1, -1, -1
    for i in range(len(vertical_lines)):
        a = False
        for j in range(i,-1, -1):
            d = vertical_lines[i] - vertical_lines[j]
            if vcell_size - 5 < d < vcell_size +5:
                a=True
                break
            elif d > vcell_size:
                break
        for j in range(i,len(vertical_lines)):
            d = vertical_lines[j] - vertical_lines[i]
            if vcell_size - 5 < d < vcell_size +5:
                a=True
                break
            elif d > vcell_size:
                break
        if a:
            vertical_mode_lines.append(vertical_lines[i])



    horizontal_lines = []
    if lines is not None: 
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(y1 - y2) < 5:   # nearly vertical
                horizontal_lines.append(y1)
    horizontal_lines = sorted(horizontal_lines)
    horizontal_lines = cluster_sorted(horizontal_lines, max_gap=10)
    distances = []
    for i in range(len(horizontal_lines) - 1):
        d = horizontal_lines[i+1] - horizontal_lines[i]
        if d > 10:  # ignore duplicates
            distances.append(d)    
    try:
        hcell_size = int(statistics.mode(distances))
    except:
        return -1, -1, -1
    horizontal_mode_lines = []
    for i in range(len(horizontal_lines)):
        a = False
        for j in range(i,-1, -1):
            d = horizontal_lines[i] - horizontal_lines[j]
            if hcell_size - 5 < d < hcell_size +5:
                a=True
                break
            elif d > hcell_size:
                break
        for j in range(i,len(horizontal_lines)):
            d = horizontal_lines[j] - horizontal_lines[i]
            if hcell_size - 5 < d < hcell_size +5:
                a=True
                break
            elif d > hcell_size:
                break
        if a:
            horizontal_mode_lines.append(horizontal_lines[i])
    for x1 in vertical_mode_lines:
        cv2.line(output, (int(x1), 0), (int(x1), int(img.shape[0])), (0,255,0), 2)
    for y1 in horizontal_mode_lines:
        cv2.line(output, (0, int(y1)), (int(img.shape[1]), int(y1)), (0,255,0), 2)
    if vcell_size -2<hcell_size < vcell_size +2:
        return round((hcell_size+vcell_size)/2), vertical_mode_lines, horizontal_mode_lines



def place_new_flag(matrix):
    rows, cols = len(matrix), len(matrix[0])
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    found=False
    probable_mines = {}
    undiged_srounding = {}
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
                        for l,q in undug_cells:
                            if probable_mines.get(l*cols+q):
                                probable_mines[l*cols+q].append(i*cols+j)
                            else:
                                probable_mines[l*cols+q] = [i*cols+j]  
                        undiged_srounding[((i*cols+j), num_mines-flagged_count)] = [p*cols+q for p,q in undug_cells]


    if not found and probable_mines:
        constraints = build_constraints(undiged_srounding)
        components = group_constraints(constraints)

        definite_mines = set()
        definite_safe = set()
        for component in components:
            mines, safe = solve_component(component)
            definite_mines |= mines
            definite_safe |= safe

        if definite_mines or definite_safe:
            for cell in definite_mines:
                i, j = divmod(cell, cols)
                matrix[i][j] = -4  # Definite mine -> flag it
            for cell in definite_safe:
                i, j = divmod(cell, cols)
                matrix[i][j] = -3  # Definite safe -> dig it
            found = True

    return matrix, found



def build_constraints(undiged_srounding):
    """
    Convert the raw {(numbered_cell, remaining_mines): [undug_cell_indices]} dict
    produced in place_new_flag into a clean list of (cells, mine_count) constraints,
    where `cells` is a frozenset of flattened undug-cell indices that must together
    contain exactly `mine_count` mines.
    """
    constraints = []
    for (_num_cell, remaining_mines), cells in undiged_srounding.items():
        cell_set = frozenset(cells)
        if cell_set:
            constraints.append((cell_set, remaining_mines))
    return constraints


def group_constraints(constraints):
    """
    Split constraints into independent connected components using union-find on
    shared cells. Constraints that don't share any cell can't influence each
    other, so solving them separately keeps each CSP small and fast.
    """
    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[ry] = rx

    for cells, _ in constraints:
        for c in cells:
            parent.setdefault(c, c)

    for cells, _ in constraints:
        cell_list = list(cells)
        for i in range(1, len(cell_list)):
            union(cell_list[0], cell_list[i])

    groups = {}
    for cells, mine_count in constraints:
        root = find(next(iter(cells)))
        groups.setdefault(root, []).append((cells, mine_count))

    return list(groups.values())


def solve_component(component_constraints, max_vars=25):
    """
    Backtracking CSP solve for one connected group of constraints.
    Each variable (undug cell) is assigned 0 (safe) or 1 (mine). A partial
    assignment is pruned as soon as any fully-assigned constraint is violated.
    Returns (definite_mines, definite_safe): the cell indices that hold the
    same value across every valid solution -- i.e. what we can act on with
    certainty. Cells that vary between solutions are left alone (unknown).
    """
    variables = sorted({c for cells, _ in component_constraints for c in cells})
    n = len(variables)

    # Guard against combinatorial blowup on large open components.
    if n == 0 or n > max_vars:
        return set(), set()

    var_index = {v: i for i, v in enumerate(variables)}

    # Check each constraint as soon as its last (highest-index) variable is set,
    # so invalid branches get cut off early instead of only at full depth.
    constraints_by_last_var = {}
    for cells, mine_count in component_constraints:
        positions = sorted(var_index[c] for c in cells)
        constraints_by_last_var.setdefault(positions[-1], []).append((positions, mine_count))

    solutions = []
    assignment = [None] * n

    def backtrack(pos):
        if pos == n:
            solutions.append(assignment.copy())
            return
        for value in (0, 1):
            assignment[pos] = value
            ok = True
            for positions, mine_count in constraints_by_last_var.get(pos, []):
                if sum(assignment[p] for p in positions) != mine_count:
                    ok = False
                    break
            if ok:
                backtrack(pos + 1)
        assignment[pos] = None

    backtrack(0)

    if not solutions:
        # Contradiction in the constraints (shouldn't normally happen with
        # correct board data) -- nothing safe to conclude, so back off.
        return set(), set()

    definite_mines = set()
    definite_safe = set()
    for i, var in enumerate(variables):
        values = {sol[i] for sol in solutions}
        if values == {1}:
            definite_mines.add(var)
        elif values == {0}:
            definite_safe.add(var)

    return definite_mines, definite_safe

        
                         

                 
                 


def find_next_dig(matrix):
    height = len(matrix)
    width = len(matrix[0])
    safe_moves = []
    
    # Check every cell in the grid
    for row in range(height):
        for col in range(width):
            if checked_matrix[row][col] == 0 and matrix[row][col] > 0:  # If it's a number cell
                covered_neighbors = []
                mine_count = 0

                # Check surrounding 8 cells
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < height and 0 <= nc < width:
                            if matrix[nr][nc] == 0:  # Covered cell
                                
                                covered_neighbors.append((nr, nc))
                            elif matrix[nr][nc] == -1 or matrix[nr][nc] == -4:  # Flagged mine
                                mine_count += 1
                
                # If the number of flagged mines matches the number, dig remaining covered cells
                if mine_count == matrix[row][col]:
                    for r,c in covered_neighbors:
                        matrix[r][c] = -3
                        print(r,c, row, col, matrix[row][col])
                    checked_matrix[row][col] = 1
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


# -------- command-line arguments --------
parser = argparse.ArgumentParser(description="Minesweeper solver")
parser.add_argument(
    '--a', type=int, default=1, choices=[0, 1],
    help="1 = auto-detect screen coordinates via screen_area.get_cordinate (default), "
         "0 = use the hardcoded fallback coordinate"
)
args = parser.parse_args()

website_name = "google_minesweeper"
colour_data = load_colour_data(website_name)
x=0

# -------- control flags --------
running = True
paused = True

# -------- keyboard handler --------
def on_press(key):
    global running, paused
    try:
        if key.char == 'q':   # stop program
            running = False
            return False      # stop listener

        if key.char == 'p':   # pause / resume toggle
            paused = not paused
            print("Paused" if paused else "Resumed")

    except AttributeError as e:
        pass
def non_zero_change(matrix_queue:list, matrix_ind:int):
    # Need at least one previous matrix
    if matrix_ind <= 0 or matrix_ind >= len(matrix_queue):
        return False

    prev = np.array(matrix_queue[matrix_ind - 1])
    curr = np.array(matrix_queue[matrix_ind])

    # Shape mismatch = definitely changed
    if prev.shape != curr.shape:
        return True

    # Compare only positions where at least one is non-zero
    mask = (prev != 0)

    return np.any(prev[mask] != curr[mask])
# -------- start keyboard listener (runs in background thread) --------

print("scroll mouse to get screen cordinate")
a = args.a
if a:
    cordinate = [0,0,100,100]
    cordinate = screen_area.get_cordinate(cordinate)
else:
    cordinate =  [1036, 296, 1820, 957] # [1106, 376, 1743, 866] #[1097, 356, 1765, 888]    # 

#cols, rows =  24, 20 #18,14 #24,20 #18,14 #map(int,input('enter number of columns and rows format(c r):-').split()) #10,8 #




image = get_screen(cordinate)

cell_size, v_lines, h_lines = get_lines(image)
if cell_size ==-1:
    raise ValueError('no roi found')
cordinate[2] += cell_size-((cordinate[2]-cordinate[0]) - v_lines[-1])
cordinate[3] += cell_size-((cordinate[3]-cordinate[1]) - h_lines[-1])
cordinate[0] -= cell_size-v_lines[0]
cordinate[1] -= cell_size-h_lines[0]


width = cordinate[2] - cordinate[0]
height = cordinate[3] - cordinate[1] 
rows = round((height)/cell_size)
cols = round((width)/cell_size)
print('cordinates:- ', cordinate, rows, cols, len(v_lines), len(h_lines))
listener = keyboard.Listener(on_press=on_press)
listener.start()
checked_matrix = [[0]*cols for i in range(rows)]
matrix_queue = [[[0]*cols for i in range(rows)] for j in range(3)]
matrix_ind = 2
recovery = 0
window_name = "gray Capture"

# create window once
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)
cv2.imshow(window_name, image)
while True:
    image = get_screen(cordinate)
    matrix_ind = (matrix_ind +1) % len(matrix_queue)
    matrix_queue[matrix_ind] = [[0]*cols for i in range(rows)]
    if x %20 == 0:
        cell_size, v_lines, h_lines = get_lines(image)
        if v_lines[0] >cell_size-5:
            v_lines.insert(0, 0)
        if image.shape[1] - v_lines[-1] > cell_size-5:
            v_lines.append(image.shape[1])
        if h_lines[0] -0 >cell_size-5:
            h_lines.insert(0, 0)
        if image.shape[0] - h_lines[-1] > cell_size-5:
            h_lines.append(image.shape[0])
    else:
        for x1 in v_lines:
            cv2.line(image, (int(x1), 0), (int(x1), int(image.shape[0])), (0,255,0), 2)
        for y1 in h_lines:
            cv2.line(image, (0, int(y1)), (int(image.shape[1]), int(y1)), (0,255,0), 2)
    #print(v_lines)
    try:
        image = divide_and_highlight_nums(image, v_lines, h_lines, matrix_queue[matrix_ind])
    except Exception as e:
        if recovery > 10:
            print(v_lines, h_lines, cell_size, rows, cols)
            print('exit after 10 recovery',e)
            cv2.imwrite('recovery.png', image)
            break
        recovery += 1
        sleep(0.2)
        continue
    nch = non_zero_change(matrix_queue, matrix_ind)
    if nch == True:
        if recovery > 5:
            print('exit after 5 recovery')
            break
        recovery += 1
        sleep(0.1)
        continue

    recovery = 0



    # show frame (window already topmost)
    #cv2.imshow(window_name, out_image)p

    matrix_queue[matrix_ind], found = place_new_flag(matrix_queue[matrix_ind])
    loc, matrix_queue[matrix_ind] = find_next_dig(matrix_queue[matrix_ind])

    image = grafic_output(image, (cols, rows), matrix_queue[matrix_ind])
    
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    cv2.imshow(window_name, rgb_image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print('asdasd')
        for row in matrix_queue[matrix_ind]:
            print(row)
        break
    if paused:
        continue

    
    
    matrix_queue[matrix_ind] = place_flag(matrix_queue[matrix_ind], cordinate, (cols, rows))
    matrix_queue[matrix_ind] = do_dig(matrix_queue[matrix_ind], cordinate, (cols, rows))
    


    x += 1
    sleep(0.5)

cv2.destroyAllWindows()