import openai
from decouple import config
from pathlib import Path
import os
import subprocess
import sys

import requests  # To check URL availability
import time  # For cache-busting timestamp


# Add the parent directory to sys.path to import sibling modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Custom function imports
from functions.database import get_recent_conversation_history

# Retrieve the API key from the .env file
organization = config("OPEN_AI_ORG")
api_key = config("OPEN_AI_KEY")
client = openai.OpenAI(api_key=api_key, organization=organization)

def get_gpt_response_vlm(transcript,image_url):
    history = get_recent_conversation_history()

    # Add a cache-busting parameter to ensure fresh requests
    image_url = f"{image_url}?cache_bust={int(time.time())}"

    # Verify URL accessibility before proceeding
    try:
        response = requests.get(image_url, timeout=20)
        if response.status_code != 200:
            print(f"Image URL {image_url} is inaccessible with status code {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error checking image URL: {e}")
        return None
    
    user_message = {"role": "user", "content": [{"type": "text", "text": transcript },{"type": "image_url", "image_url": {"url": image_url}}]}  # Correct structure for image URL
    history.append(user_message)
    #print("Updated history: ", history)
    
    try:
        # Create a stream using the OpenAI API
        stream = client.chat.completions.create(
            model="gpt-4o",
            messages=history,
            stream=True,
            max_tokens=300
        )
        response_text = ""  # Initialize an empty string to accumulate the response

        
        # Loop over the chunks from the stream
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                content = chunk.choices[0].delta.content
                response_text += content  # Accumulate the streamed content
        return response_text

    except Exception as e:
        print(e)
        return None

# Test script for get_gpt_response_vlm function

if __name__ == "__main__":
    # Define test inputs
    transcript = "This is a test message for GPT with an image. What is in the image?"
    image_url = "https://images-sunbird-dashing.ngrok-free.app/images/5e0c7ee8-9f1a-4104-b57d-a358c5fea416.jpeg"

    # Call the function with test inputs
    response = get_gpt_response_vlm(transcript, image_url)

    # Check and print the result
    if response:
        print("GPT-4 response:", response)
    else:
        print("No response received from GPT-4.")
