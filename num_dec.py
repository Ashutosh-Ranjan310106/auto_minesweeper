import cv2
import pytesseract
import numpy as np
import screen_area
from PIL import ImageGrab,Image
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
cordinate = [1104, 372, 1776, 895]
print(cordinate)
import time
time.sleep(5)
cap=ImageGrab.grab(bbox=cordinate)
image= np.array(cap)
# Convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Apply thresholding to make numbers more distinct
thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

# Find contours to detect grid cells
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Sort contours from top-left to bottom-right
def sort_contours(cnts):
    bounding_boxes = [cv2.boundingRect(c) for c in cnts]
    return [cnt for _, cnt in sorted(zip(bounding_boxes, cnts), key=lambda b: (b[0][1], b[0][0]))]

contours = sort_contours(contours)

# Define grid dimensions (adjust based on detected cells)
grid_size = (10, 10)  # Adjust this based on the game area
matrix = [[0] * grid_size[1] for _ in range(grid_size[0])]

# Process each detected cell
for i, contour in enumerate(contours):
    x, y, w, h = cv2.boundingRect(contour)
    if w > 10 and h > 10:  # Filter out small noise
        cell_roi = gray[y:y+h, x:x+w]
        text = pytesseract.image_to_string(cell_roi, config='--psm 10 -c tessedit_char_whitelist=012345678')
        text = text.strip()
        if text.isdigit():
            row, col = i // grid_size[1], i % grid_size[1]  # Adjust indexing
            matrix[row][col] = int(text)

# Print the detected matrix
for row in matrix:
    print(row)
