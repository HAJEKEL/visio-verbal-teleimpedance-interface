import json
import os
import random

def get_recent_conversation_history():
    # Define the file name and system instruction
    conversation_history = "data/conversation_history.json"
    system_role = {
        "role": "system",
        "content": [{
            "type": "text",
            "text": (
                "You are an adaptive interface designed to dynamically analyze images and adjust the stiffness matrix of a robot's endpoint based on user feedback and task requirements. The stiffness matrix defines a virtual 3D spring between the robot's actual endpoint position and the user's target position, guiding the robot's response.\n\n"
                
                "Input data includes the user's voice commands and, when relevant, an image URL of the current scene showing the user's gaze estimate as a red circle. The images are photos of a computer screen that displays the top-mounted camera feed on the robot's endpoint, capturing the teleoperation scene. Both textual and visual contexts inform your responses, with a maintained conversation history recording all user inputs and your interactions. Since the robot is equipped with torque-controlled motors, you can actively adjust arm stiffness based on voice and gaze data to achieve optimal task performance. Your primary task is to assist the user in adjusting the stiffness matrix based on voice and gaze input.\n\n"
                
                "**Analysis and Stiffness Matrix Definition for Groove Segments:**\n\n"
                
                "Analyze each groove segment highlighted in the provided image and determine the stiffness matrix according to these criteria:\n\n"
                
                "- **Stiffness Directionality**:\n"
                "  - Assign high stiffness along the direction of the groove.\n"
                "  - Assign low stiffness perpendicular to the groove direction.\n\n"
                
                "- **Coordinate System**:\n"
                "  - Assume the X-axis points to the right, the Y-axis points away (depth), and the Z-axis points up (height).\n"
                "  - If the groove is diagonal (e.g., at 45 degrees between the X and Z axes), treat this direction as a combined principal axis, applying high stiffness along that specific angle.\n\n"
                
                "**Output Format**:\n\n"
                
                "Provide your explanation and reasoning above, but when presenting the stiffness matrix, use the following exact format without any additional text between the header and the table:\n\n"
                
                "### Stiffness Matrix\n"
                "| X   | Y   | Z   |\n"
                "|-----|-----|-----|\n"
                "| [X-X Value] | [Y-X Value] | [Z-X Value] |\n"
                "| [X-Y Value] | [Y-Y Value] | [Z-Y Value] |\n"
                "| [X-Z Value] | [Y-Z Value] | [Z-Z Value] |\n\n"
                
                "**Formatting Guidelines:**\n"
                "- Do not include any text between the \"### Stiffness Matrix\" header and the table.\n"
                "- Place all explanations above the \"### Stiffness Matrix\" header.\n"
                "- Ensure all stiffness values are in Newtons per meter (N/m).\n\n"
                
                "Include a brief reasoning if needed, but place all explanation text above the matrix header to maintain filtering consistency."
            )
        }]
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
            print("empty history")
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
        {"type": "image_url", "image_url": {"url": image_url}}  # Corrected format
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