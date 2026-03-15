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
    output = img.copy() 
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 0, 10)
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi/180,
        threshold=10,
        minLineLength=20,
    )
    vertical_lines = []
    if lines is not None: 
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if abs(x1 - x2) < 5:   # nearly vertical
                vertical_lines.append(x1)
    vertical_lines = sorted(vertical_lines)
    vertical_lines = cluster_sorted(vertical_lines, max_gap=10)

    distances = []
    for i in range(len(vertical_lines) - 1):
        d = vertical_lines[i+1] - vertical_lines[i]
        if d > 10:  # ignore duplicates
            distances.append(d)    
    try:
        vcell_size = int(statistics.mode(distances))
    except:
        vcell_size = -1


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
        hcell_size = -1

    print(len(horizontal_lines), len(vertical_lines), round((hcell_size+vcell_size)/2))
    for x1 in vertical_lines:
        cv2.line(output, (int(x1), 0), (int(x1), int(img.shape[0])), (0,255,0), 2)
    for y1 in horizontal_lines:
        cv2.line(output, (0, int(y1)), (int(img.shape[1]), int(y1)), (0,255,0), 2)
    sleep(2)
    cv2.imshow("gray Capture", edges)
    cv2.imshow("gray", output)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        return True
    return round((hcell_size+vcell_size)/2), vertical_lines, horizontal_lines
def get_screen(cordinate):
    image=ImageGrab.grab(bbox=cordinate)
    image = np.array(image)
    return  image
cordinates = [1106, 376, 1743, 866]
img = get_screen(cordinates)
cell_size, v_lines, h_lines = get_lines(img)
cordinates[2] += cell_size-((cordinates[2]-cordinates[0]) - v_lines[-1])
cordinates[3] += cell_size-((cordinates[3]-cordinates[1]) - h_lines[-1])
cordinates[0] -= cell_size-v_lines[0]
cordinates[1] -= cell_size-h_lines[0]

img = get_screen(cordinates)
get_lines(img)
sleep(5)


    