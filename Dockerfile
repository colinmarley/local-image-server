FROM python:3-slim-buster

# Install system dependencies, including Tesseract OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    libgl1 \
    && apt-get clean

# Create the application directory
RUN mkdir /code

WORKDIR /code

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py upload_images.py opencv_routes.py preprocessing_routes.py /code/
COPY classes /code/classes

# Set the default command to run the FastAPI server
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8082"]