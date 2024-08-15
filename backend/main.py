from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    # This function handles GET requests to the root URL ("/")
    return {"message": "Hello World"}
