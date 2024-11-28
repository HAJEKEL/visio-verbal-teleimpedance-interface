from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Mount the directory where stiffness ellipsoid images are saved
app.mount("/ellipsoids", StaticFiles(directory="ellipsoids"), name="ellipsoids")
