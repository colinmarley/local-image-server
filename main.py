from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from upload_images import router as upload_router  # Import the router
from PIL import Image
import pytesseract
import os
from datetime import datetime

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
async def perform_ocr(image_name: str = Query(..., description="Name of the image file to process")):
    """
    Perform OCR on the specified image file and return the extracted text.
    """
    image_dir = "/images"
    image_path = os.path.join(image_dir, image_name)

    # Check if the image exists
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")

    try:
        # Open the image and perform OCR
        image = Image.open(image_path)
        extracted_text = pytesseract.image_to_string(image)

        return {
            "message": "OCR performed successfully",
            "image_name": image_name,
            "extracted_text": extracted_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process the image: {str(e)}")