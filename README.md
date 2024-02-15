# image-server
A repo to hold code for the medium article how to do an easy image server fastapi
```
DATA_DIR="$PWD/images"  
docker build -t image-server:latest .  
docker run --restart always --network host -d -v $DATA_DIR:/images image-server:latest  
```
http://localhost:8002/images/Gemini_Generated_Image.jpeg  
