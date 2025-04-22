import cv2
import os
import pytesseract
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()

@router.get("/bounding-boxes")
async def bounding_boxes(image_name: str = Query(..., description="Name of the image file to process")):
    """
    Detect text fields in the specified image and draw bounding boxes around them.
    """
    image_dir = "/images"
    bounding_dir = os.path.join(image_dir, "bounding")
    os.makedirs(bounding_dir, exist_ok=True)
    image_path = os.path.join(image_dir, image_name)

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
            if int(data["conf"][i]) > 0:  # Only consider text with confidence > 0
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