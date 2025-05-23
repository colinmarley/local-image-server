# image-server

A repo to hold code for the medium article on how to create an easy image server using FastAPI.

## Setup Instructions

1. **Set up the environment variable:**
   Create a `.env` file in the root of your project with the following content:
   ```env
   DATA_DIR=/c/Users/colin/code/image-server/images

2. **Build the Docker image:**
   ```sh
   docker-compose build
   ```

3. **Run the Docker container:**
   ```sh
   docker-compose up -d
   ```

4. **Access the API:**
   Open your browser and navigate to:
   ```
   http://localhost:8082/images/Gemini_Generated_Image.jpeg
   ```

5. **Upload Images Example**
   Example Request
   You can use curl to test the /upload endpoint:

   *Single File Upload*
   ```
   curl -X POST "http://localhost:8082/upload" \
   -F "files=@path/to/image1.jpg" \
   -F "save_location=/images/single"
   ```

   Batch File Upload
   ```
   curl -X POST "http://localhost:8082/upload" \
   -F "files=@path/to/image1.jpg" \
   -F "files=@path/to/image2.jpg" \
   -F "save_location=/images/batch"
   ```
   
6. **PaddleOCR Example**
   Example Request
   You can use curl to test the /ocr_paddle endpoint:

   ```sh
   curl -X GET "http://localhost:8082/ocr_paddle?image_name=ANNA_DVD_SLEEVE.png"
   ```

   If the image is in a subfolder, for example, `processed`:
   ```sh
   curl -X GET "http://localhost:8082/ocr_paddle?image_name=processed_timestamp_your_image.png&subfolder=processed"
   ```

   This implementation allows users to upload single or multiple images and specify the directory where they should be saved.

## Notes
- Ensure the [images](http://_vscodecontentref_/3) directory exists in your specified `DATA_DIR` and contains the images you want to serve.
- The API will be accessible at `http://localhost:8082`.

## Troubleshooting
- If you encounter issues, check the Docker container logs:
  ```sh
  docker logs <container_id>