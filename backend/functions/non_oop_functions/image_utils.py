import cv2
from PIL import Image

def smart_crop(image_path, output_path, size=(512, 512)):
    """
    Smartly crop the image to focus on the prominent object and resize to the specified size.

    Args:
        image_path (str): Path to the input image.
        output_path (str): Path to save the cropped image.
        size (tuple): The desired size (width, height) of the cropped image.
    """
    try:
        img_cv = cv2.imread(image_path)
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        # Use OpenCV to find the largest contour
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
        else:
            # Fallback to center crop if no contours are found
            print(f"No prominent object detected in {image_path}, falling back to center crop.")
            with Image.open(image_path) as img:
                x, y, w, h = 0, 0, img.width, img.height

        # Expand the bounding box slightly
        margin = 0.1
        x = max(int(x - w * margin), 0)
        y = max(int(y - h * margin), 0)
        w = min(int(w * (1 + margin * 2)), img_cv.shape[1] - x)
        h = min(int(h * (1 + margin * 2)), img_cv.shape[0] - y)

        # Crop and resize
        cropped_img = img_cv[y:y+h, x:x+w]
        cropped_resized = cv2.resize(cropped_img, size)

        # Save the processed image
        Image.fromarray(cv2.cvtColor(cropped_resized, cv2.COLOR_BGR2RGB)).save(output_path)
        print(f"Smart cropped image saved to {output_path}")
    except Exception as e:
        raise RuntimeError(f"Error during cropping: {e}")
