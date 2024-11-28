from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

app = FastAPI()

# Mount static directories for matrices and ellipsoids
app.mount("/matrices", StaticFiles(directory="matrices"), name="matrices")
app.mount("/ellipsoids", StaticFiles(directory="ellipsoids"), name="ellipsoids")

# Root endpoint for local server
@app.get("/", response_class=HTMLResponse)
def read_root():
    """
    Root endpoint describing the local matrix and ellipsoid server functionality with example usage.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Local Matrix and Ellipsoid Server</title>
    </head>
    <body>
        <h1>Welcome to the Local Matrix and Ellipsoid Server</h1>
        <p>This server provides access to stiffness matrices and ellipsoid data.</p>

        <h2>Available Endpoints</h2>
        <ul>
            <li><strong>Stiffness Matrices:</strong> <a href="/matrices" target="_blank">/matrices</a></li>
            <li><strong>Stiffness Ellipsoids:</strong> <a href="/ellipsoids" target="_blank">/ellipsoids</a></li>
        </ul>

        <h2>Example Usage</h2>
        <p>To use a stiffness matrix in Python:</p>
        <pre>
import requests

url = "http://localhost:8002/matrices/example_matrix.json"
response = requests.get(url)
if response.status_code == 200:
    matrix_data = response.json()
    print(matrix_data)
        </pre>

        <p>To use an ellipsoid file in a script:</p>
        <pre>
import requests

url = "http://localhost:8002/ellipsoids/example_ellipsoid.obj"
response = requests.get(url)
if response.status_code == 200:
    with open("example_ellipsoid.obj", "wb") as file:
        file.write(response.content)
        </pre>
    </body>
    </html>
    """
    return html_content
