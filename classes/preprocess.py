from PIL import Image, ImageFilter, ImageOps
import numpy as np
import cv2
import os
import re

directory_names = {
    "images": "/images",
    "preprocessed": "/images/preprocessed",
    "bounding": "/images/bounding",
    "processing": "/images/processing",
    "grayscale": "/images/grayscale",
    "thresholding": "/images/thresholding",
    "no_noise": "/images/no_noise",
    "morphology": "/images/morphology",
    "deskew": "/images/deskew",
    "edge_detection": "/images/edge_detection",
    "contours": "/images/contours",
    "inverted": "/images/inverted",
    "equalized": "/images/equalized",
}

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

# Tesseract works best with grayscale images. Converting the image to grayscale reduces noise and simplifies processing.
def convert_to_grayscale(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to load image: {image_path}")
        raise HTTPException(status_code=400, detail="Failed to load the image. Ensure the file exists and is a valid image.")
    # create preprocessing directory if it doesn't exist
    grayscale_dir = directory_names["grayscale"]
    os.makedirs(grayscale_dir, exist_ok=True)
    os.makedirs(os.path.dirname(grayscale_dir), exist_ok=True)
    # Convert the image to grayscale
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_image_path = os.path.join(grayscale_dir, "gray_" + os.path.basename(image_path))
    # Save the grayscale image
    cv2.imwrite(gray_image_path, gray_image)

    #return the path of the saved grayscale image
    return gray_image_path

# Thresholding converts the image to black and white, which helps Tesseract focus on the text.
def add_thresholding(image_path, type="global"):
    image = cv2.imread(image_path)
    # create thresholding directory if it doesn't exist
    thresholding_dir = directory_names["thresholding"]
    os.makedirs(os.path.dirname(thresholding_dir), exist_ok=True)
    thresh_image = None
    if type == "global":
        # Apply global thresholding
        _, thresh_image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)
    elif type == "adaptive":
        # Apply adaptive thresholding
        thresh_image = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
    else:
        raise ValueError("Invalid thresholding type. Use 'global' or 'adaptive'.")
    # Save the thresholded image
    thresholded_image_path = os.path.join(thresholding_dir, "thresh_" + os.path.basename(image_path))
    cv2.imwrite(thresholded_image_path, thresh_image)

    # Return the path of the saved thresholded image
    return thresholded_image_path

# Removing noise helps clean up the image and improves OCR accuracy:
def remove_noise(image_path, type="Median"):
    image = cv2.imread(image_path)
    # create no_noise directory if it doesn't exist
    no_noise_dir = directory_names["no_noise"]
    os.makedirs(os.path.dirname(no_noise_dir), exist_ok=True)
    no_noise_image = None
    if type == "Median":
        # removes salt-and-pepper noise
        no_noise_image = cv2.medianBlur(image, 5)
    elif type == "Gaussian":
        # smoothens the image
        no_noise_image = cv2.GaussianBlur(image, (5, 5), 0)
    else:
        raise ValueError("Invalid noise removal type. Use 'Median' or 'Gaussian'.")
    # Save the processed image
    no_noise_image_path = os.path.join(no_noise_dir, "no_noise_" + os.path.basename(image_path))
    cv2.imwrite(no_noise_image_path, no_noise_image)

    # Return the path of the saved no noise image
    return no_noise_image_path

# Morphological operations can help clean up the image further:
def morphology(image_path, order="1"):
    image = cv2.imread(image_path)
    # create processing directory if it doesn't exist
    morphology_dir = directory_names["morphology"]
    os.makedirs(os.path.dirname(morphology_dir), exist_ok=True)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    morphology_image = None
    if order == "1":
        # Apply closing operation to fill small holes in the text
        morphology_image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    elif order == "2":
        # Apply opening operation to remove small noise
        morphology_image = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
    else:
        raise ValueError("Invalid morphology order. Use '1' or '2'.")
    # Save the processed image
    morphology_image_path = os.path.join(morphology_dir, "morph_" + os.path.basename(image_path))
    cv2.imwrite(morphology_image_path, morphology_image)

    # Return the path of the saved morphology image
    return morphology_image_path

# If the text in the image is skewed, deskewing can align it horizontally for better OCR results
def deskew_image(image_path):
    image = cv2.imread(image_path)
    # create deskew directory if it doesn't exist
    deskew_dir = directory_names["deskew"]
    os.makedirs(os.path.dirname(deskew_dir), exist_ok=True)
    # Apply edge detection
    edges = cv2.Canny(image, 50, 150, apertureSize=3)
    # Find lines in the image using Hough Transform
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)
    # Calculate the angle of rotation
    angle = 0.0
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle += np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
        angle /= len(lines)
    # Rotate the image to correct the skew
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_image = cv2.warpAffine(image, M, (w, h))
    # Save the processed image
    deskewed_image_path = os.path.join(deskew_dir, "deskewed_" + os.path.basename(image_path))
    cv2.imwrite(deskewed_image_path, rotated_image)

    # Return the path of the saved deskewed image
    return deskewed_image_path

# Edge detection can help highlight text and improve OCR accuracy:
def edge_detection(image_path):
    image = cv2.imread(image_path)
    # create edge_detection directory if it doesn't exist
    edge_dir = directory_names["edge_detection"]
    os.makedirs(os.path.dirname(edge_dir), exist_ok=True)
    # Apply Canny edge detection
    edges = cv2.Canny(image, 100, 200)
    # Save the processed image
    edge_image_path = os.path.join(edge_dir, "edges_" + os.path.basename(image_path))
    cv2.imwrite(edge_image_path, edges)

    # Return the path of the saved edge detection image
    return edge_image_path

# Contours can help identify text regions in the image:
def find_contours(image_path):
    image = cv2.imread(image_path)
    # create contours directory if it doesn't exist
    contours_dir = directory_names["contours"]
    os.makedirs(os.path.dirname(contours_dir), exist_ok=True)
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Apply binary thresholding
    _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # Draw contours on the original image
    contour_image = image.copy()
    cv2.drawContours(contour_image, contours, -1, (0, 255, 0), 3)
    # Save the processed image
    contour_image_path = os.path.join(contours_dir, "contours_" + os.path.basename(image_path))
    cv2.imwrite(contour_image_path, contour_image)

    # Return the path of the saved contours image
    return contour_image_path

# Inverting colors can help improve OCR accuracy in some cases:
# Especially useful for images with light text on a dark background.
def invert_colors(image_path):
    image = cv2.imread(image_path)
    # create inverted directory if it doesn't exist
    invert_dir = directory_names["inverted"]
    os.makedirs(os.path.dirname(invert_dir), exist_ok=True)
    # Invert the colors of the image
    inverted_image = cv2.bitwise_not(image)
    # Save the processed image
    inverted_image_path = os.path.join(invert_dir, "inverted_" + os.path.basename(image_path))
    cv2.imwrite(inverted_image_path, inverted_image)

    # Return the path of the saved inverted image
    return inverted_image_path

# Histogram equalization can help improve the contrast of the image:
def equalize_hist(image_path):
    image = cv2.imread(image_path)
    # create equalized directory if it doesn't exist
    equalized_dir = directory_names["equalized"]
    os.makedirs(os.path.dirname(equalized_dir), exist_ok=True)
    # Equalize the histogram
    equalized_image = cv2.equalizeHist(image)
    # Save the processed image
    equalized_image_path = os.path.join(equalized_dir, "equalized_" + os.path.basename(image_path))
    cv2.imwrite(equalized_image_path, equalized_image)

    # Return the path of the saved equalized image
    return equalized_image_path