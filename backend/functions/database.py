import json
import os
import random

def get_recent_conversation_history():
    # Define the file name and system instruction
    conversation_history = "data/conversation_history.json"
    system_role = {
        "role": "system",
        "content": "You are an interface that adjusts the stiffness matrix of the robot enpoint based on the user's feedback. The stiffness matrix is the represents the stiffness of the virtual 3 dimensional spring between the actual position of the robot enpointand and the operators set reference position."
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
    transcription_dict = {"role": "user", "content": transcription}
    response_dict = {"role": "system", "content": response}
    recent_conversation_history.append(transcription_dict)
    recent_conversation_history.append(response_dict)
    print(recent_conversation_history)
    with open(conversation_database, 'w') as f:
        json.dump(recent_conversation_history, f)

def reset_conversation_history():
    # Define the conversation history database
    conversation_database = "data/conversation_history.json"
    # Reset the conversation history
    open(conversation_database, 'w')
    return "Conversation history has been reset."