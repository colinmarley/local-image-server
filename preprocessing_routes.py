import cv2
import os
from fastapi import APIRouter, HTTPException, Query
from classes.preprocess import (
    convert_to_grayscale,
    add_thresholding,
    remove_noise,
    morphology,
    deskew_image,
    edge_detection,
    find_contours,
    invert_colors,
    equalize_hist,
)

router = APIRouter()

IMAGE_DIR = "/images"

@router.get("/grayscale")
async def grayscale(image_name: str = Query(..., description="Name of the image file to process")):
    """
    Convert the image to grayscale.
    """
    image_path = os.path.join(IMAGE_DIR, image_name)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    try:
        processed_image_path = convert_to_grayscale(image_path)
        return {"message": "Grayscale conversion successful", "processed_image_path": processed_image_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process the image: {str(e)}")


@router.get("/thresholding")
async def thresholding(
    image_name: str = Query(..., description="Name of the image file to process"),
    type: str = Query("global", description="Thresholding type: 'global' or 'adaptive'")
):
    """
    Apply thresholding to the image.
    """
    image_path = os.path.join(IMAGE_DIR, image_name)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    try:
        processed_image_path = add_thresholding(image_path, type)
        return {"message": "Thresholding successful", "processed_image_path": processed_image_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process the image: {str(e)}")


@router.get("/remove-noise")
async def remove_noise_endpoint(
    image_name: str = Query(..., description="Name of the image file to process"),
    type: str = Query("Median", description="Noise removal type: 'Median' or 'Gaussian'")
):
    """
    Remove noise from the image.
    """
    image_path = os.path.join(IMAGE_DIR, image_name)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    try:
        processed_image_path = remove_noise(image_path, type)
        return {"message": "Noise removal successful", "processed_image_path": processed_image_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process the image: {str(e)}")


@router.get("/morphology")
async def morphology_endpoint(
    image_name: str = Query(..., description="Name of the image file to process"),
    order: str = Query("1", description="Morphology order: '1' (closing) or '2' (opening')")
):
    """
    Apply morphological transformations to the image.
    """
    image_path = os.path.join(IMAGE_DIR, image_name)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    try:
        processed_image_path = morphology(image_path, order)
        return {"message": "Morphology successful", "processed_image_path": processed_image_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process the image: {str(e)}")


@router.get("/deskew")
async def deskew(image_name: str = Query(..., description="Name of the image file to process")):
    """
    Deskew the image to align text horizontally.
    """
    image_path = os.path.join(IMAGE_DIR, image_name)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    try:
        processed_image_path = deskew_image(image_path)
        return {"message": "Deskewing successful", "processed_image_path": processed_image_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process the image: {str(e)}")


@router.get("/invert-colors")
async def invert_colors_endpoint(image_name: str = Query(..., description="Name of the image file to process")):
    """
    Invert the colors of the image.
    """
    image_path = os.path.join(IMAGE_DIR, image_name)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    try:
        processed_image_path = invert_colors(image_path)
        return {"message": "Color inversion successful", "processed_image_path": processed_image_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process the image: {str(e)}")


@router.get("/equalize-hist")
async def equalize_hist_endpoint(image_name: str = Query(..., description="Name of the image file to process")):
    """
    Equalize the histogram of the image.
    """
    image_path = os.path.join(IMAGE_DIR, image_name)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    try:
        processed_image_path = equalize_hist(image_path)
        return {"message": "Histogram equalization successful", "processed_image_path": processed_image_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process the image: {str(e)}")


@router.get("/preprocess-for-ocr")
async def preprocess_for_ocr(image_name: str = Query(..., description="Name of the image file to process")):
    """
    Apply a series of preprocessing steps to prepare the image for OCR.
    """
    image_path = os.path.join(IMAGE_DIR, image_name)
    if not os.path.exists(image_path):
        raise HTTPException(status_code=404, detail="Image not found")
    try:
        # Apply preprocessing steps in a logical order
        grayscale_image_path = convert_to_grayscale(image_path)
        thresholded_image_path = add_thresholding(grayscale_image_path, "adaptive")
        denoised_image_path = remove_noise(thresholded_image_path, "Median")
        deskewed_image_path = deskew_image(denoised_image_path)
        final_image_path = invert_colors(deskewed_image_path)

        return {"message": "Preprocessing for OCR successful", "processed_image_path": final_image_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to preprocess the image: {str(e)}")