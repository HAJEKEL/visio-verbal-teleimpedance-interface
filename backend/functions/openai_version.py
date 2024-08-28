import sys
import importlib

def import_openai_version(version_path):
    """
    Dynamically imports a specific version of the OpenAI package.
    
    Parameters:
        version_path (str): The path to the directory containing the specific version of OpenAI.
    
    Returns:
        module: The imported OpenAI module.
    """
    # Add the path to sys.path
    sys.path.insert(0, version_path)
    
    # Import the openai module
    openai = importlib.import_module("openai")
    
    # Remove the path from sys.path to avoid conflicts later
    sys.path.pop(0)
    
    return openai
