import cv2
import os
import pytesseract
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

@router.get("/preprocess")
async def preprocess_image(image_name: str = Query(..., description="Name of the image file to process")):
    """
    Preprocess the image for OCR by applying filters and resizing.
    """
    image_dir = "/images"
    processed_dir = os.path.join(image_dir, "preprocessed")
    os.makedirs(processed_dir, exist_ok=True)
    image_path = os.path.join(image_dir, image_name)

    # Ensure the output directory exists
    os.makedirs(processed_dir, exist_ok=True)

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    try:
        # Load the image
        image = cv2.imread(image_path)

        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        binary = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(binary, (5, 5), 0)

        # Resize the image (optional)
        resized = cv2.resize(blurred, (0, 0), fx=2, fy=2)

        # Save the preprocessed image
        output_image_name = f"processed_{image_name}"
        output_image_path = os.path.join(processed_dir, output_image_name)
        cv2.imwrite(output_image_path, resized)

        return {
            "message": "Image preprocessed successfully",
            "original_image": image_name,
            "output_image": output_image_name,
            "output_image_path": output_image_path,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process the image: {str(e)}")

@router.get("/bounding-boxes")
async def bounding_boxes(
    image_name: str = Query(..., description="Name of the image file to process"),
    subfolder: str = Query(None, description="Subfolder to save the output image")
):
    """
    Detect text fields in the specified image and draw bounding boxes around them.
    """
    image_dir = "/images"
    bounding_dir = os.path.join(image_dir, "bounding")
    os.makedirs(bounding_dir, exist_ok=True)
    image_path = os.path.join(image_dir, subfolder, image_name)

    # Ensure the output directory exists
    os.makedirs(bounding_dir, exist_ok=True)

    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    try:
        # Load the image
        image = cv2.imread(image_path)

        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Perform OCR with bounding box detection
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

        # Draw bounding boxes around detected text
        for i in range(len(data["text"])):
            if int(data["conf"][i]) > 80:  # Only consider text with confidence > 80
                x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Save the image with bounding boxes
        output_image_name = f"bounding_boxes_{image_name}"
        output_image_path = os.path.join(bounding_dir, output_image_name)
        cv2.imwrite(output_image_path, image)

        return {
            "message": "Bounding boxes created successfully",
            "original_image": image_name,
            "output_image": output_image_name,
            "output_image_path": output_image_path,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process the image: {str(e)}")