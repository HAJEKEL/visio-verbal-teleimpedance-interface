import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def generate_ellipsoid(stiffness_matrix):
    """
    Generates an ellipsoid plot based on the stiffness matrix.

    Parameters:
        stiffness_matrix (list): The 3x3 stiffness matrix.

    Returns:
        None: Displays the plot.
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
            print("Error: Stiffness matrix must be positive definite.")
            return

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

        plt.show()

    except Exception as e:
        print(f"Error generating ellipsoid plot: {e}")


if __name__ == "__main__":
    print("Stiffness Ellipsoid Tester")
    print("Input your stiffness matrix as a 3x3 list.")
    print("Example: [[1000, 0, 0], [0, 200, 0], [0, 0, 200]]\n")

    # Input stiffness matrix
    try:
        user_input = input("Enter your stiffness matrix: ")
        stiffness_matrix = eval(user_input)

        if len(stiffness_matrix) == 3 and all(len(row) == 3 for row in stiffness_matrix):
            generate_ellipsoid(stiffness_matrix)
        else:
            print("Error: Please enter a valid 3x3 stiffness matrix.")
    except Exception as e:
        print(f"Invalid input: {e}")
