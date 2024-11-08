import numpy as np
import matplotlib.pyplot as plt
import os
from uuid import uuid4

def generate_ellipsoid_plot(stiffness_matrix):
    try:
        # Convert input matrix to NumPy array
        K = np.array(stiffness_matrix)
    
        # Perform eigenvalue decomposition
        eigenvalues, eigenvectors = np.linalg.eigh(K)
    
        # The lengths of the ellipsoid axes are proportional to the stiffness values
        axes_lengths = eigenvalues  # Use eigenvalues directly for axes lengths
    
        # Generate ellipsoid data in the eigenbasis
        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 50)
        x = axes_lengths[0] * np.outer(np.cos(u), np.sin(v))
        y = axes_lengths[1] * np.outer(np.sin(u), np.sin(v))
        z = axes_lengths[2] * np.outer(np.ones_like(u), np.cos(v))
    
        # Rotate the ellipsoid back to the original coordinate system
        ellipsoid = np.array([x, y, z])
        ellipsoid_rotated = np.einsum('ij,jkl->ikl', eigenvectors, ellipsoid)
    
        # Plot the ellipsoid
        fig = plt.figure(figsize=(8, 8))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot_surface(
            ellipsoid_rotated[0], ellipsoid_rotated[1], ellipsoid_rotated[2],
            color='b', alpha=0.6, rstride=4, cstride=4, linewidth=0.5
        )
        ax.set_xlabel('X-axis (N/m)')
        ax.set_ylabel('Y-axis (N/m)')
        ax.set_zlabel('Z-axis (N/m)')
        ax.set_title("Stiffness Ellipsoid")
    
        # Determine the maximum stiffness value for setting the axis limits
        max_stiffness = np.max(eigenvalues)
    
        # Set the axes limits to range from -max_stiffness to +max_stiffness
        ax.set_xlim(-max_stiffness, max_stiffness)
        ax.set_ylim(-max_stiffness, max_stiffness)
        ax.set_zlim(-max_stiffness, max_stiffness)
    
        # Ensure equal scaling along all axes
        ax.set_box_aspect([1,1,1])  # Requires Matplotlib 3.3+
    
        # Ensure ellipsoids directory exists
        if not os.path.exists("ellipsoids"):
            os.makedirs("ellipsoids")
    
        # Save plot to the ellipsoids directory
        filename = f"ellipsoids/{uuid4()}.png"
        file_url = f"https://ellipsoids-sunbird-dashing.ngrok-free.app/{filename}"
        fig.savefig(filename)
        plt.close(fig)
    
        print(f"Ellipsoid plot saved as {filename}")
        return file_url
    except Exception as e:
        print(f"Error generating ellipsoid plot: {e}")
