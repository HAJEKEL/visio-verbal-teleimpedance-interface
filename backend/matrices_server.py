from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Specify the origins that are allowed to access the resources
origins = [
    "https://frontend-example.ngrok-free.app"
]

# Add CORS middleware to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,     # You can use ["*"] to allow all origins, but it's safer to specify
    allow_credentials=True,
    allow_methods=["GET"],     # Only allow GET requests
    allow_headers=["*"],
)

# Mount the matrices directory
app.mount("/matrices", StaticFiles(directory="matrices"), name="matrices")
