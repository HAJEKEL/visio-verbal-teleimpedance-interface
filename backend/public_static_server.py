import os
from dotenv import load_dotenv, find_dotenv
import logging
import sys
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# Load environment variables from .env file if not already set
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path, override=False)

# Retrieve the required environment variables
try:
    # Required variables
    FRONTEND_URL = os.environ['FRONTEND_URL']
    LOG_LEVEL = os.environ['LOG_LEVEL']

except KeyError as e:
    logging.error(f"Environment variable {e.args[0]} is not set.")
    sys.exit(1)

# Configure logging with the specified level
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s")
logging.info(f"Logging level set to {LOG_LEVEL}")


app = FastAPI()

# Configure CORS for public image server
origins = [
    FRONTEND_URL
]

# Log information about the configured CORS origins
logging.info("Configuring CORS middleware with the following allowed origins:")
for origin in origins:
    logging.info(f" - {origin}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Mount static directory for images
app.mount("/images", StaticFiles(directory="images"), name="images")

# Root endpoint for public image server
@app.get("/", response_class=HTMLResponse)
def read_root():
    """
    Root endpoint describing the public image server functionality with example usage.
    """
    # Define the path to the HTML file
    html_file_path = os.path.join(os.path.dirname(__file__), "templates", "public_static_server_root_page.html")
    
    # Read the HTML content
    try:
        with open(html_file_path, "r", encoding="utf-8") as file:
            html_content = file.read()
    except FileNotFoundError:
        return HTMLResponse(content="<h1>Error: root_page.html not found</h1>", status_code=500)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error: {e}</h1>", status_code=500)

    return HTMLResponse(content=html_content)
