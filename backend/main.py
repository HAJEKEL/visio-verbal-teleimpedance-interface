from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from decouple import config
import openai

# uvicorn main:app  # uvicorn main:app --reload
# main imports

# Initiate app
app = FastAPI()
# CORS origins that are allowed to connect to this server
# origins = [
#     "http://localhost:5173", # React dev server
#     "http://localhost:5174", # React dev server second
#     "http://localhost:4173", # React deploy server
#     "http://localhost:4174", # React deploy server second
#     "http://localhost:3000"] # General frontend application server

# # Add CORS middleware to the app
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

@app.get("/vader")
async def vader_endpoint():
    # This function handles GET requests to the /vader endpoint
    return {"message": "Ga ervoor Pa, winnen met rummikub. Je kan het!"}

@app.get("/moeder")
async def moeder_endpoint():
    # This function handles POST requests to the /moeder endpoint
    return {"message": "Ga ervoor Ma. Laat pa niet winnen!"}
