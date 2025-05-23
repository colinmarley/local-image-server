from fastapi import FastAPI, Query, HTTPException, Body
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from upload_images import router as upload_router  # Import the upload router
from opencv_routes import router as opencv_router  # Import the OpenCV router
from preprocessing_routes import router as preprocessing_router  # Import the preprocessing router
from PIL import Image
import pytesseract
import os
import json
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
app.include_router(opencv_router)
app.include_router(preprocessing_router)

@app.get("/search")
async def search_images(query: str = Query(..., min_length=1)):
    image_dir = "/images"
    matching_files = []
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            print(file)
            file_path = os.path.join(root, file)
            parent_folder = os.path.basename(root)
            last_modified = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
            if query.lower() in file.lower():
                matching_files.append({
                    "name": file,
                    "url": file_path,
                    "parent_folder": parent_folder,
                    "size": os.path.getsize(file_path),
                    "last_modified": last_modified
                })
    return {"matching_files": matching_files}

@app.get("/list")
async def list_images():
    image_dir = "/images"
    image_list = []
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            file_path = os.path.join(root, file)
            parent_folder = os.path.basename(root)
            last_modified = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
            image_list.append({
                "name": file,
                "url": file_path,
                "parent_folder": parent_folder,
                "size": os.path.getsize(file_path),
                "last_modified": last_modified
            })
    return {"images": image_list}

@app.post("/rename")
async def rename_image(current_name: str = Query(...), new_name: str = Query(...), subfolder: str = Query(None)):
    image_dir = "/images"
    current_path = os.path.join(image_dir, current_name)
    
    if subfolder:
        new_path = os.path.join(image_dir, subfolder, new_name)
        os.makedirs(os.path.dirname(new_path), exist_ok=True)
    else:
        new_path = os.path.join(image_dir, new_name)
    
    if not os.path.exists(current_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    if os.path.exists(new_path):
        raise HTTPException(status_code=400, detail="New file name already exists")
    
    os.rename(current_path, new_path)
    return {"message": "File renamed successfully", "new_path": new_path}

@app.get("/ocr")
async def perform_ocr(
    image_name: str = Query(..., description="Name of the image file to process"),
    subfolder: str = Query(None, description="Subfolder to save the output image"),
    lang: str = Query("eng", description="Language for OCR (default: 'eng')")
):
    """
    Perform OCR on the specified image file and return the extracted text.
    """
    # Get language from query parameter (default to English)
    image_dir = "/images"
    image_path = os.path.join(image_dir, image_name)
    # Check if a subfolder is provided
    if subfolder:
        image_path = os.path.join(image_dir, subfolder, image_name)
        print(image_path)
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

@app.post("/save_annotations")
async def save_annotations(annotation: dict = Body(...)):
    """
    Save bounding box annotation data sent from the UI.
    Expects JSON body: {"imageName": str, "x": int, "y": int, "width": int, "height": int}
    Appends the annotation to a JSON file (annotations.json) in the /images directory.
    """
    annotations_path = os.path.join("/images", "annotations.json")
    # Load existing annotations if file exists
    if os.path.exists(annotations_path):
        with open(annotations_path, "r", encoding="utf-8") as f:
            try:
                annotations = json.load(f)
            except Exception:
                annotations = []
    else:
        annotations = []

    # Add timestamp to annotation
    annotation["timestamp"] = datetime.now().isoformat()
    annotations.append(annotation)

    # Save back to file
    with open(annotations_path, "w", encoding="utf-8") as f:
        json.dump(annotations, f, indent=2)

    return {"message": "Annotation saved successfully", "annotation": annotation}
