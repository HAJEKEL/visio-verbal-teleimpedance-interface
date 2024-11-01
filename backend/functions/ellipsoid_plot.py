import numpy as np
import matplotlib.pyplot as plt
import os
from uuid import uuid4

def generate_ellipsoid_plot(stiffness_matrix):
    try:
        # Convert input matrix to NumPy array
        K = np.array(stiffness_matrix)

        # Perform singular value decomposition
        U, S, _ = np.linalg.svd(K)
        radii = 1 / np.sqrt(S)

        # Generate ellipsoid data
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 50)
        x = radii[0] * np.outer(np.cos(u), np.sin(v))
        y = radii[1] * np.outer(np.sin(u), np.sin(v))
        z = radii[2] * np.outer(np.ones_like(u), np.cos(v))

        # Rotate the ellipsoid
        ellipsoid = np.array([x, y, z])
        ellipsoid_rotated = np.einsum('ij,jkl->ikl', U, ellipsoid)

        # Plot the ellipsoid
        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(
            ellipsoid_rotated[0], ellipsoid_rotated[1], ellipsoid_rotated[2],
            color='b', alpha=0.6, rstride=4, cstride=4, linewidth=0.5
        )
        ax.set_xlabel('X-axis (stiffness)')
        ax.set_ylabel('Y-axis (stiffness)')
        ax.set_zlabel('Z-axis (stiffness)')
        ax.set_title("Stiffness Ellipsoid")

        # Ensure ellipsoids directory exists
        if not os.path.exists("ellipsoids"):
            os.makedirs("ellipsoids")

        # Save plot to the ellipsoids directory
        filename = f"ellipsoids/{uuid4()}.png"
        fig.savefig(filename)
        plt.close(fig)

        print(f"Ellipsoid plot saved as {filename}")

    except Exception as e:
        print(f"Error generating ellipsoid plot: {e}")
