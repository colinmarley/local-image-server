from PIL import Image, ImageFilter, ImageOps
import re

def preprocess_image(image_path):
    image = Image.open(image_path)
    # Convert to grayscale
    image = image.convert("L")
    # Apply thresholding
    image = ImageOps.autocontrast(image)
    # Resize the image (optional)
    image = image.resize((image.width * 2, image.height * 2), Image.Resampling.LANCZOS)
    # Apply filters to reduce noise
    image = image.filter(ImageFilter.MedianFilter(size=3))
    return image

def clean_text(text):
    # Remove non-alphanumeric characters
    text = re.sub(r"[^a-zA-Z0-9\s.,]", "", text)
    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()
    return text