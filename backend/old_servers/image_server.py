from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Mount the images directory
app.mount("/images", StaticFiles(directory="images"), name="images")
