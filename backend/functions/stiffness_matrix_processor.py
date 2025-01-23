import os
import re
import json
import uuid
import logging
import numpy as np
import matplotlib.pyplot as plt
import commentjson

class StiffnessMatrixProcessor:
    """
    A class to process stiffness matrices:
    - Extracts stiffness matrices from a response string.
    - Validates and saves the matrix to a file.
    - Generates an ellipsoid plot based on the stiffness matrix.
    """

    def __init__(
        self,
        use_public_urls=False,
        matrices_base_url=None,
        ellipsoids_base_url=None,
        local_static_server_port=None,
        matrices_dir='matrices',
        ellipsoids_dir='ellipsoids'
    ):
        """
        Initializes the processor with optional base URLs and directories.

        Parameters:
            use_public_urls (bool): Flag to determine whether to use public or local URLs.
            matrices_base_url (str): The base URL used to construct matrix file URLs.
            ellipsoids_base_url (str): The base URL used to construct ellipsoid plot URLs.
            matrices_dir (str): Directory where matrices are saved.
            ellipsoids_dir (str): Directory where ellipsoid plots are saved.
        """
        self.use_public_urls = use_public_urls
        self.matrices_dir = matrices_dir
        self.ellipsoids_dir = ellipsoids_dir

        # Set base URLs based on the use_public_urls flag
        if self.use_public_urls:
            # Use public domains if use_public_urls is True
            self.matrices_base_url = 'https://matrices-sunbird-dashing.ngrok-free.app'
            self.ellipsoids_base_url = 'https://ellipsoids-sunbird-dashing.ngrok-free.app'
        else:
            # Use localhost or provided base URLs
            self.matrices_base_url = matrices_base_url or f"http://localhost:{local_static_server_port}"
            self.ellipsoids_base_url = ellipsoids_base_url or f"http://localhost:{local_static_server_port}"

        # Ensure base URLs do not have trailing slashes
        self.matrices_base_url = self.matrices_base_url.rstrip('/')
        self.ellipsoids_base_url = self.ellipsoids_base_url.rstrip('/')

        self.ensure_directories()

    def ensure_directories(self):
        """
        Ensures that the required directories exist.
        """
        os.makedirs(self.matrices_dir, exist_ok=True)
        os.makedirs(self.ellipsoids_dir, exist_ok=True)

    def extract_stiffness_matrix(self, response):
        """
        Extracts the stiffness matrix from a response string and saves it to a file.

        Parameters:
            response (str): The response string containing the stiffness matrix in a JSON code block.

        Returns:
            tuple: A tuple containing the stiffness matrix and the URL to the saved matrix file.
        """
        # Define the pattern to extract the JSON code block
        pattern = r"```json\n(.*?)\n```"
        match = re.search(pattern, response, re.DOTALL)

        if not match:
            logging.error("No JSON code block found in the response.")
            return None, None

        json_code = match.group(1)

        try:
            # Parse the JSON code with comments
            data = commentjson.loads(json_code)
            stiffness_matrix = data.get('stiffness_matrix')

            if stiffness_matrix is None:
                logging.error("Key 'stiffness_matrix' not found in JSON data.")
                return None, None

            # Validate the stiffness matrix structure
            if not self.validate_stiffness_matrix(stiffness_matrix):
                return None, None

            # Save stiffness matrix to a file
            matrix_filename = f"{uuid.uuid4()}.json"
            matrix_file_path = os.path.join(self.matrices_dir, matrix_filename)

            with open(matrix_file_path, "w") as matrix_file:
                json.dump(stiffness_matrix, matrix_file)

            # Generate URL for the matrix file
            matrix_file_url = f"{self.matrices_base_url}/{self.matrices_dir}/{matrix_filename}"
            logging.info(f"Stiffness matrix extracted and saved: {stiffness_matrix}")

            return stiffness_matrix, matrix_file_url

        except commentjson.JSONLibraryException as e:
            logging.error(f"Error parsing JSON with comments: {e}")
            return None, None
    
    def rotate_stiffness_camera_to_ee(self, stiffness_matrix):
        """
        Rotates the given 3x3 stiffness matrix from the camera frame
        to the end-effector frame by applying a 90° rotation about Z.

        Parameters:
            stiffness_matrix (list): A 3x3 stiffness matrix in camera frame.

        Returns:
            list: The transformed 3x3 stiffness matrix in end-effector frame.
        """
        # Convert input to a NumPy array
        K_cam = np.array(stiffness_matrix, dtype=float)

        # Define the rotation matrix for +90° about Z:
        #   Rz(90°) = [[ 0, -1,  0],
        #              [ 1,  0,  0],
        #              [ 0,  0,  1]]
        Rz_90 = np.array([
            [0, -1,  0],
            [1,  0,  0],
            [0,  0,  1]
        ], dtype=float)

        # Transform stiffness: K_ee = R * K_cam * R^T
        K_ee = Rz_90 @ K_cam @ Rz_90.T

        # Convert back to a Python list of lists
        return K_ee.tolist()

    def validate_stiffness_matrix(self, matrix):
        """
        Validates that the stiffness matrix is a 3x3 matrix.

        Parameters:
            matrix (list): The stiffness matrix to validate.

        Returns:
            bool: True if valid, False otherwise.
        """
        if len(matrix) != 3:
            logging.error(f"Expected 3 rows in stiffness_matrix, found {len(matrix)}.")
            return False

        for i, row in enumerate(matrix):
            if len(row) != 3:
                logging.error(f"Expected 3 values in row {i}, found {len(row)}.")
                return False

        return True

    def generate_ellipsoid_plot(self, stiffness_matrix):
        """
        Generates an ellipsoid plot based on the stiffness matrix and saves it to a file.

        Parameters:
            stiffness_matrix (list): The 3x3 stiffness matrix.

        Returns:
            str: The URL to the saved ellipsoid plot image.
        """
        try:
            # Convert input matrix to NumPy array
            K = np.array(stiffness_matrix, dtype=float)

            # Perform eigenvalue decomposition
            eigenvalues, eigenvectors = np.linalg.eigh(K)

            # Sort eigenvalues and eigenvectors in descending order
            idx = eigenvalues.argsort()[::-1]
            eigenvalues = eigenvalues[idx]
            eigenvectors = eigenvectors[:, idx]

            # Check for positive eigenvalues
            if np.any(eigenvalues <= 0):
                logging.error("Stiffness matrix must be positive definite.")
                return None

            # The lengths of the ellipsoid axes are proportional to the square roots of eigenvalues
            axes_lengths = np.sqrt(eigenvalues)

            # Generate ellipsoid data
            u = np.linspace(0, 2 * np.pi, 100)
            v = np.linspace(0, np.pi, 50)
            x = axes_lengths[0] * np.outer(np.cos(u), np.sin(v))
            y = axes_lengths[1] * np.outer(np.sin(u), np.sin(v))
            z = axes_lengths[2] * np.outer(np.ones_like(u), np.cos(v))

            # Rotate the ellipsoid
            ellipsoid = np.array([x, y, z])
            ellipsoid_rotated = np.einsum('ij,jkl->ikl', eigenvectors, ellipsoid)

            # Plot the ellipsoid
            fig = plt.figure(figsize=(8, 8))
            ax = fig.add_subplot(111, projection='3d')
            ax.plot_surface(
                ellipsoid_rotated[0], ellipsoid_rotated[1], ellipsoid_rotated[2],
                color='b', alpha=0.6, rstride=4, cstride=4, linewidth=0.5
            )
            ax.set_xlabel('X-axis')
            ax.set_ylabel('Y-axis')
            ax.set_zlabel('Z-axis')
            ax.set_title("Stiffness Ellipsoid")

            # Ensure equal scaling along all axes
            max_radius = np.max(axes_lengths)
            ax.set_box_aspect([1, 1, 1])
            ax.auto_scale_xyz(
                [-max_radius, max_radius],
                [-max_radius, max_radius],
                [-max_radius, max_radius]
            )

            # Save plot to the ellipsoids directory
            filename = f"{uuid.uuid4()}.png"
            file_path = os.path.join(self.ellipsoids_dir, filename)
            fig.savefig(file_path)
            plt.close(fig)

            # Generate URL for the plot
            file_url = f"{self.ellipsoids_base_url}/{self.ellipsoids_dir}/{filename}"
            logging.info(f"Ellipsoid plot saved as {file_path}")

            return file_url

        except Exception as e:
            logging.error(f"Error generating ellipsoid plot: {e}")
            return None


if __name__ == "__main__":
    # Initialize the processor
    processor = StiffnessMatrixProcessor(use_public_urls=True)

    # Test stiffness matrix in the camera frame
    test_matrix = [[100, 0, 0], [0, 1000, 0], [0, 0, 100]]

    print("Original Stiffness Matrix (Camera Frame):")
    for row in test_matrix:
        print(row)

    # Transform the matrix to the end-effector frame
    rotated_matrix = processor.rotate_stiffness_camera_to_ee(test_matrix)

    print("\nRotated Stiffness Matrix (End-Effector Frame):")
    for row in rotated_matrix:
        print(row)

    # Verify expected output
    # Expected transformation:
    # Rotation of +90 degrees about Z axis swaps X and Y axes with a sign flip on Y.
    # Expected matrix:
    # [[   0, -100,    0],
    #  [ 100,    0,    0],
    #  [   0,    0,  100]]
