from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

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

@app.get("/search")
async def search_images(query: str = Query(..., min_length=1)):
    image_dir = "/images"
    matching_files = []
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            print(file)
            if query.lower() in file.lower():
                matching_files.append(os.path.join(root, file))
    return {"matching_files": matching_files}

@app.get("/list")
async def list_images():
    image_dir = "/images"
    image_list = []
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            image_list.append({
                "name": file,
                "url": os.path.join(root, file)
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
