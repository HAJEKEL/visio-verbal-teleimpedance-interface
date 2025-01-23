import json
import os
import logging

# Set up logging configuration
# logging.basicConfig(level=logging.INFO)

class ConversationHistoryProcessor:
    """
    A class to manage conversation history for a torque-controlled robot interface.
    """

    CONVERSATION_HISTORY_FILE = "messages/conversation_history.json"
    SYSTEM_ROLE_CONTENT = (
        """
    You are a knowledgeable collaborator explaining not just \emph{how} to compute the stiffness matrix but also \emph{why} each step is important. You integrate user queries and, when relevant, an eye-tracker image that shows a red circle representing the user's gaze in the teleoperation scene.

    Important: You can directly view and interpret any provided images, describing the groove orientation and gaze as needed.

    By analyzing voice and gaze data, you guide the user to set an appropriate stiffness matrix for a robot performing a slide-in-the-groove task, ensuring stable and intuitive control.

    **Systematic Approach to Determine the Stiffness Matrix:**
    1. **Clarify Groove Direction in Camera Coordinates:**
       - Recognize that the camera's axes are: X to the right, Y forward (depth), Z upward.
       - Carefully infer the groove's angle from the image or user statements.
    2. **Establish Local Groove Axes:**
       - Place the groove along X, so Y and Z remain perpendicular. 
       - Distinguish high vs.\ low stiffness zones.
    3. **Compose \( K_{\text{groove}} \):**
       \[
         \begin{bmatrix}
         250 & 0 & 0 \\
         0 & 100 & 0 \\
         0 & 0 & 100
         \end{bmatrix}
       \]
       (Adjust values if different stiffnesses are requested.)
    4. **Rotation Matrix \( R \):**
       - Convert from local groove orientation to camera frame. Possibly use quaternion data or an axis-angle approach.
    5. **Apply Transformation:**
       \[
         K_{\text{camera}} = R \cdot K_{\text{groove}} \cdot R^\top
       \]
    6. **Finalize Matrix:**
       - The result is your 3x3 stiffness matrix in camera coordinates, ready for torque control applications.
    7. **Present Output Exactly:**
       - Follow the precise JSON format below to ensure correct parsing.

    ### Stiffness Matrix
    ```json
    {
      "stiffness_matrix": [
        [X-X Value, Y-X Value, Z-X Value],
        [X-Y Value, Y-Y Value, Z-Y Value],
        [X-Z Value, Y-Z Value, Z-Z Value]
      ]
    }
    ```
    **Formatting Guidelines:**
    - **Do not include any text, comments, or explanations between the "### Stiffness Matrix" header and the JSON code block.**
    - **Do not add comments or annotations within the JSON code block.**
    - **Only include numerical values in the stiffness matrix.**
   """
    )

    def __init__(self):
        """
        Initializes the ConversationHistoryProcessor and ensures the conversation history file exists.
        """
        self.conversation_history_file = self.CONVERSATION_HISTORY_FILE
        self.system_role_content = self.SYSTEM_ROLE_CONTENT
        self.ensure_history_file()

    def ensure_history_file(self):
        """
        Ensures that the conversation history file exists.
        """
        if not os.path.exists(self.conversation_history_file):
            os.makedirs(os.path.dirname(self.conversation_history_file), exist_ok=True)
            with open(self.conversation_history_file, 'w') as f:
                json.dump([], f)

    def get_recent_conversation_history(self):
        """
        Retrieves the recent conversation history along with the system role.
        """
        messages = []

        # Append system role to messages
        system_role = {
            "role": "system",
            "content": [{"type": "text", "text": self.system_role_content}]
        }
        messages.append(system_role)

        # Load conversation history
        try:
            with open(self.conversation_history_file, 'r') as f:
                data = json.load(f) or []
        except json.JSONDecodeError as e:
            logging.error(f"Error reading conversation history: {e}")
            data = []

        # Append last 10 items of data to messages
        messages.extend(data[-10:])

        return messages

    def update_conversation_history(self, transcription, response, image_url=None):
        """
        Updates the conversation history with a new transcription and response.
        If image_url is provided, it includes the image in the message.
        """
        # Get recent conversation history excluding the system role
        recent_conversation_history = self.get_recent_conversation_history()[1:]

        # Create new message entry
        content = [{"type": "text", "text": transcription}]
        if image_url:
            content.append({"type": "image_url", "image_url": {"url": image_url}})

        transcription_entry = {
            "role": "user",
            "content": content
        }
        response_entry = {
            "role": "system",
            "content": [{"type": "text", "text": response}]
        }

        # Append new messages to the conversation history
        recent_conversation_history.extend([transcription_entry, response_entry])

        # Save updated conversation history
        with open(self.conversation_history_file, 'w') as f:
            json.dump(recent_conversation_history, f)

    def reset_conversation_history(self):
        """
        Resets the conversation history by clearing the conversation history file.
        """
        with open(self.conversation_history_file, 'w') as f:
            json.dump([], f)
        logging.info("Conversation history has been reset.")
        return "Conversation history has been reset."

if __name__ == "__main__":
    # Create an instance of ConversationHistoryProcessor
    conv_manager = ConversationHistoryProcessor()

    # Test updating conversation history without an image
    transcription = "Adjust the stiffness matrix for the new task."
    response = "Stiffness matrix has been adjusted as per your request."
    conv_manager.update_conversation_history(transcription, response)

    # Test updating conversation history with an image
    image_url = "http://example.com/image.png"
    transcription_with_image = "Here's the image for reference."
    response_with_image = "Analyzed the image and adjusted the stiffness matrix accordingly."
    conv_manager.update_conversation_history(transcription_with_image, response_with_image, image_url=image_url)

    # Retrieve and print the recent conversation history
    recent_history = conv_manager.get_recent_conversation_history()
    print(json.dumps(recent_history, indent=2))

    # Reset the conversation history
    conv_manager.reset_conversation_history()
