import openai
from decouple import config
from pathlib import Path
import os
import subprocess


# Retrieve the API key from the .env file
organization = config("OPEN_AI_ORG")
api_key = config("OPEN_AI_KEY")
client = openai.OpenAI(api_key=api_key, organization=organization)


response = client.chat.completions.create(
  model="gpt-4o-mini",
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": "what is in the image"
            },
            {
                "type": "image_url",
                "image_url": {  # Nest the image URL within an `image_url` dictionary
                    "url": "https://images-sunbird-dashing.ngrok-free.app/images/4e12db7a-a065-434e-ae5f-21b29c29846c.png"
                }
            }
        ]
    },
    {
        "role": "system",
        "content": [
            {
                "type": "text",
                "text": "The image shows an empty room with light-colored walls and a wooden floor. There's a window on the right side showing some greenery outside. In the center of the wall, there's a small red dot or object."
            }
        ]
    }
],
  max_tokens=300,
)
print(response.choices[0])