from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from upload_images import router as upload_router  # Import the router
from PIL import Image
import pytesseract
import os
from datetime import datetime
from classes.preprocess import preprocess_image, clean_text  # Import the preprocess function
from classes.categorize import categorize_text  # Import the categorize function

# Set the Tesseract executable path (optional if installed in the default path)
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

app = FastAPI()

# Allow all origins for CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.mount("/images", StaticFiles(directory="/images"), name='images')

# Include the upload route from upload.py
app.include_router(upload_router)

@app.get("/ocr")
async def perform_ocr(
    image_name: str = Query(..., description="Name of the image file to process"),
    lang: str = Query("eng", description="Language for OCR (default: 'eng')")
):
    """
    Perform OCR on the specified image file and return the extracted text.
    """
    # Get language from query parameter (default to English)
    image_dir = "/images"
    image_path = os.path.join(image_dir, image_name)
    # extracted_text = pytesseract.image_to_string(image)
    # extracted_text = pytesseract.image_to_string(image, lang=lang)

    # You can pass custom configurations to Tesseract to improve accuracy. For example:
    # --psm (Page Segmentation Mode): Controls how Tesseract interprets the layout of the text.
    # --oem (OCR Engine Mode): Specifies the OCR engine to use.
    # config = "--psm 6 --oem 3"
    # extracted_text = pytesseract.image_to_string(image, config=config)

    # Check if the image exists
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    try:
        # Initialize the image variable
        image = None

         # Preprocess the image
        try:
            image = preprocess_image(image_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to preprocess the image: {str(e)}")

        # Perform OCR
        try:
            extracted_text_unclean = pytesseract.image_to_string(image, lang=lang)
            extracted_text = clean_text(extracted_text_unclean)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to perform OCR: {str(e)}")

        # Save the processed image with a timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        processed_image_name = f"processed_{timestamp}_{image_name}"
        processed_image_path = os.path.join(image_dir + "/processed", processed_image_name)
        
        # Ensure the processed directory exists
        os.makedirs(os.path.dirname(processed_image_path), exist_ok=True)

        # Save the processed image
        try:
            image.save(processed_image_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save the processed image: {str(e)}")

        # Categorize the text
        try:
            categories = categorize_text(extracted_text)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to categorize the text: {str(e)}")

        return {
            "message": "OCR performed successfully",
            "image_name": image_name,
            "extracted_text": extracted_text,
            "categories": categories,
            "processed_image_name": processed_image_name,
            "processed_image_path": processed_image_path,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process the image: {str(e)}")