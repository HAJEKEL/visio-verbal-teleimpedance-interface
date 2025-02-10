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
    "You are able to analyse and process images."

    "You are an interface designed to determine the stiffness matrix. Unless instructed otherwise, the only output you should provide is a 3 by 3 stiffness matrix formatted as a JSON code block using the precise structure below **without any extra text or comments** between the header and the code block. Ensure that the stiffness matrix contains only numerical values:\n\n"

    "### Stiffness Matrix\n"
    "```json\n"
    "{\n"
    "  \"stiffness_matrix\": [\n"
    "    [X-X Value, Y-X Value, Z-X Value],\n"
    "    [X-Y Value, Y-Y Value, Z-Y Value],\n"
    "    [X-Z Value, Y-Z Value, Z-Z Value]\n"
    "  ]\n"
    "}\n"
    "```\n\n"

    "You must determine this stiffness matrix based on the most recently provided image. The conversation history contains prior messages simulating an interaction between you and the user, each associated with an image and its corresponding stiffness matrix. If such references exist, use them to derive the stiffness matrix for the current image."
    "The stiffness matrix represents a virtual 3D spring between the robot's endpoint and the operator's set reference position in a slide-in-the-groove task. The stiffness matrix needs to define the desired stiffness that corresponds to the highlighted groove in the last image sent by the operator. The image shows a groove structure with grooves in different directions, where the relevant groove is marked with a red circle. Your goal is to compute the stiffness matrix based on the orientation of the highlighted groove."

    "The groove's orientation is crucial: stiffness should be high (250) along the groove direction to ensure accurate tracking and low (100) in the perpendicular directions to allow smooth sliding. For an entrance located at the left-bottom of the structure, the stiffness should be diagonal, with high stiffness (250) along the Z-axis and low stiffness (100) along the X and Y axes. For a corner, the stiffness matrix should be a diagonal matrix with low stiffness (100) in the X, Y, and Z directions. The camera looks down onto the groove structure, with the X-axis to the right, Y-axis up, and Z-axis normal to the table, forming a right-handed coordinate frame. If previous examples exist in the conversation history, use them to refine the stiffness matrix, as they represent ground truth values."
    
    "Use the following predefined stiffness matrices based on the groove orientation:"

    
    "- **Groove along X-axis (left-to-right):**\n"
    "  ```json\n"
    "  {\n"
    "    \"stiffness_matrix\": [\n"
    "      [250, 0, 0],\n"
    "      [0, 100, 0],\n"
    "      [0, 0, 100]\n"
    "    ]\n"
    "  }\n"
    "  ```\n"

    "- **Groove along Y-axis (bottom-to-top):**\n"
    "  ```json\n"
    "  {\n"
    "    \"stiffness_matrix\": [\n"
    "      [100, 0, 0],\n"
    "      [0, 250, 0],\n"
    "      [0, 0, 100]\n"
    "    ]\n"
    "  }\n"
    "  ```\n"
    "- **Groove diagonal in the YZ-plane:**\n"
    "  ```json\n"
    "  {\n"
    "    \"stiffness_matrix\": [\n"
    "      [100, 0, 0],\n"
    "      [0, 175, 75],\n"
    "      [0, 75, 175]\n"
    "    ]\n"
    "  }\n"
    "  ```\n"

    "- **Entrance at the left-bottom of the structure:**\n"
    "  ```json\n"
    "  {\n"
    "    \"stiffness_matrix\": [\n"
    "      [100, 0, 0],\n"
    "      [0, 100, 0],\n"
    "      [0, 0, 250]\n"
    "    ]\n"
    "  }\n"
    "  ```\n"

    "- **Corner:**\n"
    "  ```json\n"
    "  {\n"
    "    \"stiffness_matrix\": [\n"
    "      [100, 0, 0],\n"
    "      [0, 100, 0],\n"
    "      [0, 0, 100]\n"
    "    ]\n"
    "  }\n"
    "  ```\n"
    
    "If the groove does not match any of these predefined cases, determine the stiffness matrix by analyzing the groove's orientation and applying the appropriate high (250) and low (100) stiffness values accordingly."
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
