import cv2
import numpy as np
from PIL import ImageGrab
import screen_area  # Assuming this is a custom module for getting screen coordinates
    # Add colour data for specific colors
colour_data = {
    "blue": np.array([25, 118, 210]),
    "green": np.array([60, 143, 63]),
    "red": np.array([212, 54, 53]),
    "purple": np.array([123, 31, 162]),    
    "orange": np.array([242, 54, 7]),  
    "beige1": np.array([229, 194, 159]),
    "beige2": np.array([215, 184, 153]),  
}
def divide_and_highlight_nums(img, rows, cols):
    h, w, _ = img.shape
    cell_h, cell_w = h // rows, w // cols

    # Define green color range in HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_green = np.array([40, 40, 40])
    upper_green = np.array([80, 255, 255])

    for i in range(rows):
        for j in range(cols):
            y1, y2 = i * cell_h+4, (i + 1) * cell_h-4
            x1, x2 = j * cell_w+4, (j + 1) * cell_w-4
            cell_hsv = hsv[y1:y2, x1:x2]
            found_color = None
            for name, bgr in colour_data.items():
                # Convert BGR to HSV for comparison
                hsv_color = cv2.cvtColor(np.uint8([[bgr]]), cv2.COLOR_BGR2HSV)[0][0]
                lower = np.clip(hsv_color - np.array([1, 1, 1]), 0, 255)
                upper = np.clip(hsv_color + np.array([1, 1, 1]), 0, 255)
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
                else:
                    color_bgr = colour_data[found_color].tolist()
                cv2.rectangle(img, (x1, y1), (x2, y2), color_bgr, 4)

    return img

if __name__ == "__main__":
    a=0
    if a:
        cordinate = screen_area.get_cordinate()
    else:
        cordinate =  [1065, 310, 1816, 935] #[1065, 310, 1816, 935] # [1097, 356, 1781, 888]    #[1065, 310, 1816, 935]
    print(cordinate)


    w,h =  24,20 #18,14 #10,8 #24,20
    rows, cols = h,w
    #size = round(((cordinate[2] - cordinate[0])/cols + (cordinate[3] - cordinate[1])/rows)/2)
    #print(f"Size: {size}")
    # Adjust coordinates so that the width and height are divisible by cols and rows, respectively
    width = cordinate[2] - cordinate[0]
    height = cordinate[3] - cordinate[1]

    # Calculate the nearest greater width and height divisible by cols and rows
    new_width = ((width) // cols) * cols
    new_height = ((height) // rows) * rows

    # Adjust the bottom-right coordinates
    cordinate[2] = cordinate[0] + new_width
    cordinate[3] = cordinate[1] + new_height

    print(f"Adjusted Cordinate: {cordinate}")
    while True:
        image=ImageGrab.grab(bbox=cordinate)
        image = np.array(image)
  # Set desired number of rows and columns
        result = divide_and_highlight_nums(image, rows, cols)
        cv2.imshow('Green Cells Highlighted', result)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()