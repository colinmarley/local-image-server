from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
 
app = FastAPI()
 
app.mount("/images", StaticFiles(directory="/images"), name='images')


