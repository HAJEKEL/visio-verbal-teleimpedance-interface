import openai
from decouple import config
from pathlib import Path
import os
import subprocess


# Custom function imports
#from functions.database import get_recent_conversation_history

# Retrieve the API key from the .env file
organization = config("OPEN_AI_ORG")
api_key = config("OPEN_AI_KEY")
client = openai.OpenAI(api_key=api_key, organization=organization)

def get_gpt_response_vlm(transcript,image_url):
    history = get_recent_conversation_history()
    user_message = {"role": "user", "content": [{"type": "text", "text": transcript },{"type": "image_url", "image_url": {"url": image_url}}]}  # Correct structure for image URL
    history.append(user_message)
    print(history)
    
    try:
        # Create a stream using the OpenAI API
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
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