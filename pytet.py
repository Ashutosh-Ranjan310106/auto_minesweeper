import pytesseract
from PIL import Image

# Path to your image file
image_path = r'imgs\cap2_20250630_084030_308251.png'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'

# Open the image using PIL
img = Image.open(image_path)

# Extract text from image using pytesseract
text = pytesseract.image_to_string(img)

print(text)