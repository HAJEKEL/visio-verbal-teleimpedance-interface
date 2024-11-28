from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI()

# Configure CORS (update origins as needed)
origins = [
    "https://frontend-example.ngrok-free.app",
    "http://localhost:5173",
    "http://localhost:5174"
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

# Root endpoint with HTML response
@app.get("/", response_class=HTMLResponse)
def read_root():
    """
    Root endpoint describing the static files server functionality in a styled HTML format.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Static Files Server</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 20px;
                padding: 0;
                background-color: #f9f9f9;
                color: #333;
            }
            h1 {
                color: #4CAF50;
            }
            ul {
                list-style: none;
                padding: 0;
            }
            li {
                margin-bottom: 10px;
            }
            a {
                color: #4CAF50;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <h1>Welcome to the Static Files Server</h1>
        <p>This server hosts static files for images, stiffness matrices, and stiffness ellipsoids.</p>
        
        <h2>Available Static Directories</h2>
        <ul>
            <li>
                <strong>Images:</strong> 
                <a href="/images" target="_blank">/images</a> - Access uploaded or generated images.
            </li>
            <li>
                <strong>Stiffness Matrices:</strong> 
                <a href="/matrices" target="_blank">/matrices</a> - Access stiffness matrix files.
            </li>
            <li>
                <strong>Stiffness Ellipsoids:</strong> 
                <a href="/ellipsoids" target="_blank">/ellipsoids</a> - Access stiffness ellipsoid files.
            </li>
        </ul>

        <h2>Usage Instructions</h2>
        <p>Click on the links above to browse the respective directories. Use these static files in other applications as needed by referencing their URLs.</p>
    </body>
    </html>
    """
    return html_content
