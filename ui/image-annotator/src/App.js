import React, { useState, useEffect } from 'react';
import ReactCrop from 'react-image-crop';
import 'react-image-crop/dist/ReactCrop.css';

function App() {
  const [images, setImages] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);
  const [crop, setCrop] = useState({ aspect: 16 / 9 });
  const [completedCrop, setCompletedCrop] = useState(null);
  const [imageRef, setImageRef] = useState(null);

  useEffect(() => {
    // Fetch images from the backend
    fetch('http://localhost:8082/list') // Assuming the FastAPI backend serves images at /images
      .then(res => res.json())
      .then(data => {
        console.log(data)
        setImages(data.images)
      }) // Assuming the API returns { "images": ["image1.jpg", "image2.png"] }
      .catch(err => console.error("Failed to fetch images:", err));
  }, []);

  const handleImageSelect = (imageName) => {
    setSelectedImage(`/images/${imageName}`); // Assuming images are served directly from the /images route
    setCompletedCrop(null); // Reset crop when new image is selected
  };

  const onImageLoaded = image => {
    setImageRef(image);
  };

  const makeClientCrop = async (crop) => {
    if (imageRef && crop.width && crop.height) {
      const croppedImageUrl = await getCroppedImg(
        imageRef,
        crop,
        'newFile.jpeg' // This name can be dynamic
      );
      console.log('Cropped image URL:', croppedImageUrl); // For now, just log it
      // Here you would typically upload the cropped image or send coordinates
    }
  };
  
  // Utility function to get cropped image data (you might need to adjust this based on how you want to handle the crop)
  // This is a simplified version.
  function getCroppedImg(image, crop, fileName) {
    const canvas = document.createElement('canvas');
    const scaleX = image.naturalWidth / image.width;
    const scaleY = image.naturalHeight / image.height;
    canvas.width = crop.width;
    canvas.height = crop.height;
    const ctx = canvas.getContext('2d');

    ctx.drawImage(
      image,
      crop.x * scaleX,
      crop.y * scaleY,
      crop.width * scaleX,
      crop.height * scaleY,
      0,
      0,
      crop.width,
      crop.height
    );

    // For Tesseract/OpenCV, you'll want the coordinates relative to the original image.
    // The `crop` object from react-image-crop might be in percentages or pixels
    // depending on its configuration. Ensure you convert them to absolute pixel values
    // for the original image dimensions if necessary.
    console.log('Saving crop coordinates (x, y, width, height):', crop.x, crop.y, crop.width, crop.height);
    // Example: Save to local storage or send to backend
    // localStorage.setItem('boundingBox', JSON.stringify({x: crop.x, y: crop.y, width: crop.width, height: crop.height}));


    return new Promise((resolve, reject) => {
      // canvas.toBlob(blob => {
      //   if (!blob) {
      //     console.error('Canvas is empty');
      //     return;
      //   }
      //   blob.name = fileName;
      //   window.URL.revokeObjectURL(this.fileUrl); // Revoke previous URL
      //   this.fileUrl = window.URL.createObjectURL(blob);
      //   resolve(this.fileUrl);
      // }, 'image/jpeg');
      resolve("data:image/jpeg;base64,..."); // Placeholder for actual blob handling
    });
  }


  const handleSaveCrop = () => {
    if (!completedCrop || !imageRef) {
      alert('Please select an area to crop first.');
      return;
    }
    const cropDataForBackend = {
      imageName: selectedImage.split('/').pop(),
      x: Math.round(completedCrop.x),
      y: Math.round(completedCrop.y),
      width: Math.round(completedCrop.width),
      height: Math.round(completedCrop.height),
    };

    fetch('http://localhost:8082/save_annotations', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(cropDataForBackend),
    })
      .then(response => response.json())
      .then(data => {
        alert(`Bounding Box Saved (for ${cropDataForBackend.imageName}):\nX: ${cropDataForBackend.x}, Y: ${cropDataForBackend.y}\nWidth: ${cropDataForBackend.width}, Height: ${cropDataForBackend.height}`);
        console.log('Annotation saved:', data);
      })
      .catch(error => {
        alert('Error saving annotation. See console for details.');
        console.error('Error saving annotation:', error);
      });
  };


  return (
    <div className="App">
      <header className="App-header">
        <h1>Image Annotator</h1>
        <div>
          <h2>Select an Image:</h2>
          {images.length > 0 ? (
            <ul>
              {images.map(imgName => (
                <li key={imgName.url} onClick={() => handleImageSelect(imgName.name)} style={{cursor: 'pointer'}}>
                  {imgName.name}
                </li>
              ))}
            </ul>
          ) : (
            <p>Loading images or no images found in /images directory on the backend.</p>
          )}
        </div>

        {selectedImage && (
          <div>
            <h2>Annotate:</h2>
            <ReactCrop
              src={selectedImage}
              crop={crop}
              onChange={c => setCrop(c)}
              onComplete={c => setCompletedCrop(c)}
              onImageLoaded={onImageLoaded}
            />
            <button onClick={handleSaveCrop} style={{marginTop: '10px'}}>
              Save Bounding Box
            </button>
          </div>
        )}

        {completedCrop && (
          <div>
            <h3>Preview (Cropped Area Coordinates):</h3>
            <p>X: {Math.round(completedCrop.x)}px, Y: {Math.round(completedCrop.y)}px</p>
            <p>Width: {Math.round(completedCrop.width)}px, Height: {Math.round(completedCrop.height)}px</p>
            {/* You could also display the cropped image itself if getCroppedImg was fully implemented to return an image URL */}
          </div>
        )}
      </header>
    </div>
  );
}

export default App;
