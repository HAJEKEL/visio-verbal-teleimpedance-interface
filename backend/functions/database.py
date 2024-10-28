import json
import os
import random

def get_recent_conversation_history():
    # Define the file name and system instruction
    conversation_history = "data/conversation_history.json"
    system_role = {
        "role": "system",
        "content": [{"type": "text", "text": "You are a responsive interface designed to adjust the stiffness matrix of a robot endpoint according to user feedback. The stiffness matrix defines a virtual 3D spring between the robot's actual endpoint position and the user's target position, guiding the robot's response. You may receive either just the transcript of the user's voice input or both a transcript and an image URL representing the current scene. You can process both text and image data, so use visual context when available. Conversation history is maintained in this interface, recording all user inputs and your responses. Use this context to provide responses that are informed by previous interactions."}] 
    }

    # Initialize messages
    messages = []

    # Append system role to messages
    messages.append(system_role)

    # Get conversation history
    try:
        if not os.path.exists(conversation_history):
            raise FileNotFoundError(f"File {conversation_history} does not exist.")
        
        if os.path.getsize(conversation_history) == 0:
            print("Conversation history file is empty.")
        else:
            with open(conversation_history) as f:
                data = json.load(f)
            # Append last 10 items of data to messages
            if data:
                if len(data) < 10:
                    messages.extend(data)
                else:
                    messages.extend(data[-10:])    
    except Exception as e:
        print("Error reading conversation history", e)
    return messages

def update_conversation_history(transcription,response):
    # Define the conversation history database
    conversation_database = "data/conversation_history.json"
    # Get the 10 last messages
    recent_conversation_history = get_recent_conversation_history()[1:]
    # Append the new message
    transcription_dict = {"role": "user", "content": [{"type": "text", "text": transcription}]}
    response_dict = {"role": "system", "content": response}
    recent_conversation_history.append(transcription_dict)
    recent_conversation_history.append(response_dict)
    with open(conversation_database, 'w') as f:
        json.dump(recent_conversation_history, f)

def update_conversation_history_vlm(transcription,image_url,response):
    # Define the conversation history database
    conversation_database = "data/conversation_history.json"
    # Get the 10 last messages
    recent_conversation_history = get_recent_conversation_history()[1:]
    # Append the new message
    transcription_image_dict = {
        "role": "user",
        "content": [
            {"type": "text", "text": transcription},
            {"type": "image_url", "url": image_url}  # Corrected format for image URL
        ]
    }
    response_dict = {"role": "system", "content": response}    
    recent_conversation_history.append(transcription_image_dict)
    recent_conversation_history.append(response_dict)
    with open(conversation_database, 'w') as f:
        json.dump(recent_conversation_history, f)

def reset_conversation_history():
    # Define the conversation history database
    conversation_database = "data/conversation_history.json"
    # Reset the conversation history
    open(conversation_database, 'w')
    return "Conversation history has been reset."