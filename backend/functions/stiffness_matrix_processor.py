import os
import re
import json
import uuid
import logging
import numpy as np
import matplotlib.pyplot as plt
import commentjson
from itertools import permutations


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

        # --- SET GLOBAL MATPLOTLIB PARAMETERS HERE ---
        plt.rcParams['figure.figsize'] = (8, 8)        # Default figure size
        plt.rcParams['font.size'] = 14                 # Base font size
        plt.rcParams['axes.labelsize'] = 14            # Axis label size
        plt.rcParams['axes.titlesize'] = 16            # Title size
        plt.rcParams['xtick.labelsize'] = 12           # Tick label size (x-axis)
        plt.rcParams['ytick.labelsize'] = 12           # Tick label size (y-axis)
        plt.rcParams['legend.fontsize'] = 12           # Legend font size (if used)

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
        pattern = r"json\n(.*?)\n"
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
    
    def extract_stiffness_matrix_2(self, response):
        """
        Extracts the stiffness matrix from a response string and saves it to a file.

        Parameters:
            response (str): The response string containing the stiffness matrix in a JSON code block.

        Returns:
            tuple: A tuple containing the stiffness matrix and the URL to the saved matrix file.
        """
        # Improved regex pattern to extract JSON block
        pattern = r"```json\n(.*?)\n```"
        match = re.search(pattern, response, re.DOTALL)

        if not match:
            logging.error("No JSON code block found in the response.")
            return None, None

        json_code = match.group(1).strip()

        try:
            # Parse the extracted JSON
            data = json.loads(json_code)
            stiffness_matrix = data.get("stiffness_matrix")

            if stiffness_matrix is None:
                logging.error("Key 'stiffness_matrix' not found in JSON data.")
                return None, None

            # Validate the stiffness matrix structure
            if not self.validate_stiffness_matrix(stiffness_matrix):
                return None, None

            logging.info(f"Extracted Stiffness Matrix: {stiffness_matrix}")
            return stiffness_matrix, None  # Returning None for file URL for now

        except json.JSONDecodeError as e:
            logging.error(f"Error parsing extracted JSON: {e}")
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
            str: The URL to the saved ellipsoid plot image, or None on error.
        """
        try:
            # Convert input to NumPy array
            K = np.array(stiffness_matrix, dtype=float)

            # Perform eigen-decomposition (symmetric => use eigh)
            eigenvalues, eigenvectors = np.linalg.eigh(K)

            # Sort by descending eigenvalues
            idx = eigenvalues.argsort()[::-1]
            eigenvalues = eigenvalues[idx]
            eigenvectors = eigenvectors[:, idx]  # columns match the sorted eigenvalues

            # Quick check: must be positive definite
            if np.any(eigenvalues <= 0):
                logging.error("Stiffness matrix must be positive definite.")
                return None

            # ----------------------------------------------------------------------
            # 1) For each eigenvector (column), check if it's "aligned" with X, Y, or Z.
            #    - If so, and it's negative along that axis, flip it.
            #    - We do NOT reorder columns; we only do sign flips so the ellipsoid shape stays correct.
            # ----------------------------------------------------------------------

            # Threshold for "close to an axis" (could be 0.99, 0.999, etc.):
            threshold = 0.999

            # eigenvectors.shape = (3,3) => eigenvectors[:,0] is the 1st eigenvector, etc.
            for i in range(3):
                vec = eigenvectors[:, i]
                # Find which global axis has the largest absolute component
                main_axis = np.argmax(np.abs(vec))  # 0->X, 1->Y, 2->Z
                # Check if that largest component is "close" to 1 in magnitude:
                if np.abs(vec[main_axis]) > threshold:
                    # If it's negative, flip this entire eigenvector
                    if vec[main_axis] < 0:
                        eigenvectors[:, i] = -vec

            # ----------------------------------------------------------------------
            # 2) Ensure a right-handed coordinate system
            #    If the determinant is negative, flip the last eigenvector
            # ----------------------------------------------------------------------
            if np.linalg.det(eigenvectors) < 0:
                eigenvectors[:, 2] = -eigenvectors[:, 2]

            # ----------------------------------------------------------------------
            # 3) Construct the ellipsoid data using the (already sorted) eigenvalues
            # ----------------------------------------------------------------------
            u = np.linspace(0, 2 * np.pi, 100)
            v = np.linspace(0, np.pi, 50)

            # If your ellipsoid is truly "1 / sqrt(eigenvalue)" or something, adjust here.
            # We keep it simple: scale by eigenvalues directly, as in your original code.
            x = eigenvalues[0] * np.outer(np.cos(u), np.sin(v))
            y = eigenvalues[1] * np.outer(np.sin(u), np.sin(v))
            z = eigenvalues[2] * np.outer(np.ones_like(u), np.cos(v))

            ellipsoid_local = np.array([x, y, z])  # shape = (3, 100, 50)

            # Rotate the ellipsoid into global coordinates
            ellipsoid_global = np.einsum('ij,jkl->ikl', eigenvectors, ellipsoid_local)

            # ----------------------------------------------------------------------
            # 4) Plot the ellipsoid
            # ----------------------------------------------------------------------
            fig = plt.figure(figsize=(8, 8))
            ax = fig.add_subplot(111, projection='3d')

            ax.plot_surface(
                ellipsoid_global[0],
                ellipsoid_global[1],
                ellipsoid_global[2],
                color='b',
                alpha=0.2,  # Increase transparency
                rstride=4,
                cstride=4,
                linewidth=0.5
            )

            # Plot the principal axes as quivers from the origin
            colors = ['r', 'g', 'b']  # X=red, Y=green, Z=blue
            for i in range(3):
                ax.quiver(
                    0, 0, 0,
                    eigenvalues[i] * eigenvectors[0, i],
                    eigenvalues[i] * eigenvectors[1, i],
                    eigenvalues[i] * eigenvectors[2, i],
                    color=colors[i],
                    arrow_length_ratio=0.1,
                    linewidth=3
                )

            ax.set_xlabel('X-axis')
            ax.set_ylabel('Y-axis')
            ax.set_zlabel('Z-axis')
            ax.set_title("Stiffness Ellipsoid")

            # Enforce equal scaling on all axes
            max_radius = np.max(eigenvalues)
            ax.set_box_aspect([1, 1, 1])
            ax.auto_scale_xyz(
                [-max_radius, max_radius],
                [-max_radius, max_radius],
                [-max_radius, max_radius]
            )

            # ----------------------------------------------------------------------
            # 5) Save the figure
            # ----------------------------------------------------------------------
            filename = f"{uuid.uuid4()}.png"
            file_path = os.path.join(self.ellipsoids_dir, filename)
            fig.savefig(file_path)
            plt.close(fig)

            file_url = f"{self.ellipsoids_base_url}/{self.ellipsoids_dir}/{filename}"
            logging.info(f"Ellipsoid plot saved as {file_path}")

            return file_url

        except Exception as e:
            logging.error(f"Error generating ellipsoid plot: {e}")
            return None




if __name__ == "__main__":
    # Initialize the processor (can use local or public URLs)
    processor = StiffnessMatrixProcessor()

    # Define sample 3x3 stiffness matrices
    example_matrices = [
        [[100, 0, 0], [0, 100, 0], [0, 0, 250]],  # Stiff along Z
        [[100, 0, 0], [0, 100, 0], [0, 0, 100]],  # Isotropic stiffness
        [[250, 0, 0], [0, 100, 0], [0, 0, 100]],  # Stiff along X
        [[100, 0, 0], [0, 250, 0], [0, 0, 100]],  # Stiff along Y
        [[100, 0, 0], [0, 175, -75], [0, -75, 175]]  # Off-diagonal coupling
    ]

    for idx, mat in enumerate(example_matrices):
        print(f"\n--- Stiffness Matrix #{idx+1} (Camera Frame) ---")
        for row in mat:
            print(row)

        # Generate and save the stiffness ellipsoid plot
        stiffness_ellipsoid_url = processor.generate_ellipsoid_plot(mat)
        print(f"Stiffness Ellipsoid URL: {stiffness_ellipsoid_url}")