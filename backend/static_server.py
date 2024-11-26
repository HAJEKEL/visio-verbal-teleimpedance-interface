from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS (update origins as needed)
origins = [
    "https://frontend-example.ngrok-free.app"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Mount static directories for images, matrices, and ellipsoids
app.mount("/images", StaticFiles(directory="images"), name="images")
app.mount("/matrices", StaticFiles(directory="matrices"), name="matrices")
app.mount("/ellipsoids", StaticFiles(directory="ellipsoids"), name="ellipsoids")
