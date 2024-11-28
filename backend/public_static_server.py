from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI()

# Configure CORS for public image server
origins = [
    "https://frontend-example.ngrok-free.app",
    "http://localhost:5173",
]
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
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Public Image Server</title>
    </head>
    <body>
        <h1>Welcome to the Public Image Server</h1>
        <p>This server provides access to public images.</p>

        <h2>Available Endpoint</h2>
        <ul>
            <li><strong>Images:</strong> <a href="/images" target="_blank">/images</a> - Browse uploaded images.</li>
        </ul>

        <h2>Example Usage</h2>
        <p>To display an image on your website, include the following in your HTML:</p>
        <pre>
&lt;img src="https://your-public-url/images/example.jpg" alt="Example Image"&gt;
        </pre>
        <p>Replace <code>example.jpg</code> with the name of the image you uploaded.</p>

        <p>To programmatically fetch an image in JavaScript:</p>
        <pre>
fetch("https://your-public-url/images/example.jpg")
    .then(response => response.blob())
    .then(imageBlob => {
        const imageUrl = URL.createObjectURL(imageBlob);
        document.querySelector("img").src = imageUrl;
    });
        </pre>
    </body>
    </html>
    """
    return html_content
