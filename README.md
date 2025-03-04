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

## Notes
- Ensure the [images](http://_vscodecontentref_/3) directory exists in your specified `DATA_DIR` and contains the images you want to serve.
- The API will be accessible at `http://localhost:8082`.

## Troubleshooting
- If you encounter issues, check the Docker container logs:
  ```sh
  docker logs <container_id>