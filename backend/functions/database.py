import json
import random

def get_conversation_history():
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
        pass
    return messages