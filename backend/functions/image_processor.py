import os
import logging
import cv2
from PIL import Image

# Set up logging configuration
logging.basicConfig(level=logging.INFO)

class ImageProcessor:
    """
    A class to handle image processing tasks such as smart cropping.
    """

    def __init__(self):
        pass  # No initialization parameters needed for now

    def smart_crop(self, image_path, output_path, size=(512, 512)):
        """
        Smartly crop the image to focus on the prominent object and resize to the specified size.

        Parameters:
            image_path (str): Path to the input image.
            output_path (str): Path to save the cropped image.
            size (tuple): The desired size (width, height) of the cropped image.

        Returns:
            bool: True if the image was processed successfully, False otherwise.
        """
        try:
            # Check if the input image exists
            if not os.path.isfile(image_path):
                logging.error(f"Input image not found: {image_path}")
                return False

            # Read the image using OpenCV
            img_cv = cv2.imread(image_path)
            if img_cv is None:
                logging.error(f"Failed to read image: {image_path}")
                return False

            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

            # Use OpenCV to find the largest contour
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)
                logging.info(f"Largest contour found with bounding box: x={x}, y={y}, w={w}, h={h}")
            else:
                # Fallback to center crop if no contours are found
                logging.warning(f"No prominent object detected in {image_path}, falling back to center crop.")
                with Image.open(image_path) as img:
                    width, height = img.width, img.height
                    x, y, w, h = 0, 0, width, height

            # Expand the bounding box slightly
            margin = 0.1
            x = max(int(x - w * margin), 0)
            y = max(int(y - h * margin), 0)
            w = min(int(w * (1 + margin * 2)), img_cv.shape[1] - x)
            h = min(int(h * (1 + margin * 2)), img_cv.shape[0] - y)
            logging.info(f"Expanded bounding box: x={x}, y={y}, w={w}, h={h}")

            # Crop and resize
            cropped_img = img_cv[y:y+h, x:x+w]
            cropped_resized = cv2.resize(cropped_img, size)
            logging.info(f"Image cropped and resized to {size}")

            # Save the processed image
            Image.fromarray(cv2.cvtColor(cropped_resized, cv2.COLOR_BGR2RGB)).save(output_path)
            logging.info(f"Smart cropped image saved to {output_path}")

            return True

        except Exception as e:
            logging.error(f"Error during cropping: {e}")
            return False
    
    # image_processor.py

import os
import logging
import uuid
from fastapi import UploadFile
from PIL import Image
import cv2

# Set up logging configuration
logging.basicConfig(level=logging.INFO)


class ImageProcessor:
    """
    A class to handle image processing tasks such as smart cropping and image uploading.
    """

    def __init__(self, images_dir="images"):
        self.images_dir = images_dir
        os.makedirs(self.images_dir, exist_ok=True)

    def smart_crop(self, image_path, output_path, size=(512, 512)):
        """
        Smartly crop the image to focus on the prominent object and resize to the specified size.

        Parameters:
            image_path (str): Path to the input image.
            output_path (str): Path to save the cropped image.
            size (tuple): The desired size (width, height) of the cropped image.

        Returns:
            bool: True if the image was processed successfully, False otherwise.
        """
        try:
            # Read the image using OpenCV
            img_cv = cv2.imread(image_path)
            if img_cv is None:
                logging.error(f"Failed to read image: {image_path}")
                return False

            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

            # Use OpenCV to find the largest contour
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)
                logging.info(f"Largest contour found with bounding box: x={x}, y={y}, w={w}, h={h}")
            else:
                # Fallback to center crop if no contours are found
                logging.warning(f"No prominent object detected in {image_path}, falling back to center crop.")
                height, width = img_cv.shape[:2]
                x, y, w, h = 0, 0, width, height

            # Expand the bounding box slightly
            margin = 0.1
            x = max(int(x - w * margin), 0)
            y = max(int(y - h * margin), 0)
            w = min(int(w * (1 + margin * 2)), img_cv.shape[1] - x)
            h = min(int(h * (1 + margin * 2)), img_cv.shape[0] - y)
            logging.info(f"Expanded bounding box: x={x}, y={y}, w={w}, h={h}")

            # Crop and resize
            cropped_img = img_cv[y:y+h, x:x+w]
            cropped_resized = cv2.resize(cropped_img, size)
            logging.info(f"Image cropped and resized to {size}")

            # Save the processed image
            Image.fromarray(cv2.cvtColor(cropped_resized, cv2.COLOR_BGR2RGB)).save(output_path)
            logging.info(f"Smart cropped image saved to {output_path}")

            return True

        except Exception as e:
            logging.error(f"Error during cropping: {e}")
            return False

    async def process_uploaded_image(self, upload_file: UploadFile, base_url: str, size=(512, 512)) -> str:
        """
        Processes an uploaded image file: saves it temporarily, applies smart cropping,
        saves the final image, and returns the URL to the final image.

        Parameters:
            upload_file (UploadFile): The uploaded image file.
            base_url (str): The base URL to use when generating the file URL.
            size (tuple): The desired size (width, height) of the cropped image.

        Returns:
            str: The URL to the final processed image, or None if processing failed.
        """
        try:
            # Generate a unique filename
            file_extension = os.path.splitext(upload_file.filename)[-1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            temp_path = os.path.join(self.images_dir, f"temp_{unique_filename}")
            final_path = os.path.join(self.images_dir, unique_filename)

            # Save the uploaded file temporarily
            with open(temp_path, "wb") as buffer:
                file_content = await upload_file.read()
                buffer.write(file_content)
            logging.info(f"Uploaded file saved temporarily at {temp_path}")

            # Apply smart cropping and save the final image
            success = self.smart_crop(temp_path, final_path, size=size)
            if not success:
                logging.error(f"Smart cropping failed for {temp_path}")
                os.remove(temp_path)  # Clean up the temporary file
                return None
            logging.info(f"Smart cropped image saved at {final_path}")

            # Remove the temporary file
            os.remove(temp_path)
            logging.info(f"Temporary file {temp_path} removed")

            # Generate the file URL
            file_url = f"{base_url}/{self.images_dir}/{unique_filename}"
            logging.info(f"File URL generated: {file_url}")

            return file_url

        except Exception as e:
            logging.error(f"Error processing uploaded image: {e}")
            return None


if __name__ == "__main__":
    # Example usage of the ImageProcessor class
    processor = ImageProcessor()

    # Paths to input and output images
    input_image_path = "path/to/your/input_image.jpg"
    output_image_path = "path/to/save/cropped_image.jpg"

    # Perform smart cropping
    success = processor.smart_crop(input_image_path, output_image_path)
    if success:
        print(f"Image processed and saved to {output_image_path}")
    else:
        print("Image processing failed.")
