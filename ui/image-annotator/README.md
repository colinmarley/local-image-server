# Image Annotator UI

## Purpose

This React application provides a user interface for selecting images from a backend server, displaying them, and drawing bounding boxes around areas of interest (specifically, areas containing text). The goal is to capture coordinates for these bounding boxes in a format suitable for OCR (Optical Character Recognition) tools like Tesseract and image processing libraries like OpenCV.

## How it Currently Works

1.  **Image Listing**: On load, the application attempts to fetch a list of available image filenames from the backend `/images` endpoint.
2.  **Image Selection**: Users can click on an image filename from the list to select it.
3.  **Image Display**: The selected image is displayed in the interface. It assumes images are served from a path like `/images/{imageName}` on the backend.
4.  **Bounding Box Annotation**: Users can draw a rectangular bounding box on the displayed image using the `react-image-crop` library.
5.  **Coordinate Logging**: When the "Save Bounding Box" button is clicked, the application logs the pixel coordinates (x, y, width, height) of the drawn bounding box to the browser's console. An alert also displays these coordinates.

## Endpoints Used (Assumed Backend Implementation)

*   **`GET /images`**:
    *   **Purpose**: To retrieve a list of available image filenames.
    *   **Expected Response Format**: JSON, e.g., `{"images": ["image1.jpg", "image2.png", "ANNA_DVD_SLEEVE.png"]}`
*   **`GET /images/{imageName}`**:
    *   **Purpose**: To retrieve the actual image file. This is typically handled by configuring the backend (e.g., FastAPI) to serve static files from the directory where images are stored, mapping it to the `/images` route.
    *   **Example**: If `ANNA_DVD_SLEEVE.png` is selected, the UI attempts to load `http://<your-backend-url>/images/ANNA_DVD_SLEEVE.png`.
*   **`POST /save_annotations`** (Placeholder):
    *   **Purpose**: Intended for sending the bounding box coordinates and the associated image name to the backend for storage or further processing. This endpoint is not currently called by the UI but is a planned integration.
    *   **Expected Request Body Format**: JSON, e.g., `{"imageName": "ANNA_DVD_SLEEVE.png", "x": 100, "y": 150, "width": 300, "height": 50}`

## Pending Changes & Suggestions for Improvement

### Backend (FastAPI)
1.  **Implement `GET /images` Endpoint**: Create an endpoint in `main.py` that lists all image files from the `c:/Users/colin/code/image-server/images/` directory.
2.  **Serve Static Image Files**: Ensure the FastAPI application is configured to serve static files from the `images` directory, making them accessible via a route like `/images/{filename}`.
3.  **Implement `POST /save_annotations` Endpoint**: Create an endpoint to receive bounding box data (image name, x, y, width, height) and store it (e.g., in a JSON file, database, or alongside the images).
4.  **Coordinate System for OCR**: Ensure the saved coordinates are what Tesseract/OpenCV expect. This usually means coordinates relative to the *original* image dimensions. The current UI provides pixel coordinates based on the displayed image; if the image is scaled in the browser, these might need adjustment.

### Frontend (React UI - `image-annotator`)
1.  **Send Annotations to Backend**: Uncomment and complete the `fetch` call in `handleSaveCrop` in `App.js` to send the `cropDataForBackend` to the `/save_annotations` endpoint.
2.  **Error Handling**: Implement more robust error handling for API calls (e.g., if images fail to load or annotations fail to save).
3.  **User Feedback**: Provide better user feedback (e.g., loading indicators, success/error messages for saving annotations).
4.  **Coordinate Transformation (if needed)**: If the displayed image size can differ from the original image size, implement logic to transform the crop coordinates to be relative to the original image dimensions before sending them to the backend. The `imageRef.naturalWidth` and `imageRef.naturalHeight` can be used for this.
5.  **Multiple Bounding Boxes**: Extend functionality to allow drawing and saving multiple bounding boxes for a single image.
6.  **Visualizing Saved Annotations**: Load and display existing annotations for an image when it is selected.
7.  **Cropped Image Preview**: Fully implement the `getCroppedImg` function to display a preview of the selected crop area (currently, it only logs coordinates and returns a placeholder).
8.  **Integration with OCR**: Add a button or mechanism to send the selected image and its bounding box(es) to an OCR endpoint (e.g., the `/ocr_paddle` endpoint) and display the results.
9.  **Styling and UI/UX**: Improve the overall look and feel of the application.
10. **Configuration**: Allow configuration of the backend URL if it's not served from the same origin.

## Running the UI

1.  Navigate to the `c:/Users/colin/code/image-server/ui/image-annotator` directory.
2.  Install dependencies: `npm install`
3.  Start the development server: `npm start`
4.  Ensure the FastAPI backend server (from `c:/Users/colin/code/image-server`) is also running and configured to serve images and handle the necessary endpoints.

This UI is a starting point for a more comprehensive image annotation tool.
