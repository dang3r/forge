import numpy as np
from skimage import measure
import trimesh
import matplotlib.pyplot as plt


def mandelbulb(h, w, d, max_iter=10, power=8, bailout=2):
    """
    Generate a 3D Mandelbulb fractal

    Parameters:
    - h, w, d: dimensions of the 3D grid
    - max_iter: maximum iterations for escape time algorithm
    - power: power parameter for the Mandelbulb (8 is classic)
    - bailout: escape radius
    """
    # Create coordinate arrays
    x = np.linspace(-1.2, 1.2, w)
    y = np.linspace(-1.2, 1.2, h)
    z = np.linspace(-1.2, 1.2, d)

    # Create 3D meshgrid
    X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

    # Initialize arrays
    c_x, c_y, c_z = X.copy(), Y.copy(), Z.copy()
    x_new, y_new, z_new = np.zeros_like(X), np.zeros_like(Y), np.zeros_like(Z)

    # Escape time array
    escape_count = np.zeros(X.shape, dtype=int)

    print("Computing Mandelbulb fractal...")
    for i in range(max_iter):
        if i % 2 == 0:
            print(f"Iteration {i}/{max_iter}")

        # Convert to spherical coordinates
        r = np.sqrt(x_new**2 + y_new**2 + z_new**2)
        theta = np.arccos(
            z_new / (r + 1e-10)
        )  # Add small epsilon to avoid division by zero
        phi = np.arctan2(y_new, x_new)

        # Mandelbulb iteration in spherical coordinates
        r_new = r**power
        theta_new = theta * power
        phi_new = phi * power

        # Convert back to cartesian coordinates
        x_new = r_new * np.sin(theta_new) * np.cos(phi_new) + c_x
        y_new = r_new * np.sin(theta_new) * np.sin(phi_new) + c_y
        z_new = r_new * np.cos(theta_new) + c_z

        # Check for escape
        r_escaped = np.sqrt(x_new**2 + y_new**2 + z_new**2)
        escaped = r_escaped > bailout
        escape_count[escaped & (escape_count == 0)] = i

        # Stop iterating for escaped points
        mask = ~escaped
        x_new = x_new * mask
        y_new = y_new * mask
        z_new = z_new * mask

    # Points that never escaped are part of the set
    escape_count[escape_count == 0] = max_iter

    return escape_count


def create_mesh_from_fractal(fractal_data, threshold=None, smoothing_iterations=1):
    """
    Create a 3D mesh from fractal data using marching cubes
    """
    if threshold is None:
        # Use a threshold that captures the fractal boundary
        threshold = np.max(fractal_data) * 0.8

    print(f"Creating mesh with threshold: {threshold}")

    # Use marching cubes to extract isosurface
    vertices, faces, _, _ = measure.marching_cubes(
        fractal_data,
        level=threshold,
        spacing=(
            2.4 / fractal_data.shape[0],
            2.4 / fractal_data.shape[1],
            2.4 / fractal_data.shape[2],
        ),
        allow_degenerate=False,
    )

    # Center the mesh
    vertices -= np.mean(vertices, axis=0)

    # Create trimesh object
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

    # Optional: smooth the mesh
    if smoothing_iterations > 0:
        mesh = mesh.smoothed(iterations=smoothing_iterations)

    # Make sure mesh is watertight for 3D printing
    mesh.fill_holes()
    mesh.remove_duplicate_faces()
    mesh.remove_degenerate_faces()
    mesh.remove_unreferenced_vertices()

    return mesh


def generate_mandelbulb_stl(
    resolution=64, filename="mandelbulb.stl", power=8, max_iter=10, scale_factor=1.0
):
    """
    Generate a Mandelbulb fractal and save as STL file for 3D printing

    Parameters:
    - resolution: grid resolution (higher = more detail, but slower)
    - filename: output STL filename
    - power: Mandelbulb power parameter
    - max_iter: maximum iterations
    - scale_factor: factor to scale the mesh (1.0 = original size)
    """
    print(f"Generating {resolution}x{resolution}x{resolution} Mandelbulb...")

    # Generate fractal data
    fractal = mandelbulb(
        resolution, resolution, resolution, max_iter=max_iter, power=power
    )

    # Create mesh
    mesh = create_mesh_from_fractal(fractal, threshold=max_iter * 0.9)

    # Scale the mesh
    if scale_factor != 1.0:
        print(f"Scaling mesh by factor: {scale_factor}")
        mesh.apply_transform(trimesh.transformations.scale_matrix(scale_factor))

    print(f"Mesh created: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
    print(f"Mesh is watertight: {mesh.is_watertight}")
    print(f"Mesh volume: {mesh.volume:.4f}")

    # Save to STL
    mesh.export(filename)
    print(f"Saved to {filename}")

    return mesh


def generate_other_fractals():
    """
    Examples of other 3D fractals you can generate
    """

    # Mandelbox (different fractal)
    def mandelbox(size=64, scale=2.0, iterations=10):
        # Simplified mandelbox implementation
        x = np.linspace(-2, 2, size)
        y = np.linspace(-2, 2, size)
        z = np.linspace(-2, 2, size)
        X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

        c_x, c_y, c_z = X.copy(), Y.copy(), Z.copy()

        for i in range(iterations):
            # Box fold
            X = np.where(X > 1, 2 - X, X)
            X = np.where(X < -1, -2 - X, X)
            Y = np.where(Y > 1, 2 - Y, Y)
            Y = np.where(Y < -1, -2 - Y, Y)
            Z = np.where(Z > 1, 2 - Z, Z)
            Z = np.where(Z < -1, -2 - Z, Z)

            # Sphere fold
            r2 = X**2 + Y**2 + Z**2
            X = np.where(r2 < 0.25, X * 4, X)
            Y = np.where(r2 < 0.25, Y * 4, Y)
            Z = np.where(r2 < 0.25, Z * 4, Z)

            X = np.where((r2 >= 0.25) & (r2 < 1), X / r2, X)
            Y = np.where((r2 >= 0.25) & (r2 < 1), Y / r2, Y)
            Z = np.where((r2 >= 0.25) & (r2 < 1), Z / r2, Z)

            # Scale and translate
            X = scale * X + c_x
            Y = scale * Y + c_y
            Z = scale * Z + c_z

        return np.sqrt(X**2 + Y**2 + Z**2)

    return mandelbox


# Example usage
if __name__ == "__main__":
    # Generate a Mandelbulb STL file
    # Start with lower resolution for testing, increase for final print

    print("=== Generating Mandelbulb ===")
    for res in [32, 64, 128]:
        for max_iter in [3, 10, 12]:
            mesh = generate_mandelbulb_stl(
                resolution=res,  # Start small for testing
                filename=f"mandelbulb_test_{res}_{max_iter}.stl",
                power=8,
                max_iter=max_iter,
                scale_factor=1.0,
            )

    # For higher quality final print:
    # mesh = generate_mandelbulb_stl(
    #     resolution=128,
    #     filename="mandelbulb_highres.stl",
    #     power=8,
    #     max_iter=15
    # )

    print("\n=== Tips for 3D Printing ===")
    print("1. Start with resolution=32 for testing")
    print("2. Use resolution=64-128 for final prints")
    print("3. Check that mesh.is_watertight = True")
    print("4. Scale the model in your slicer software")
    print("5. Add supports if needed for overhangs")
    print("6. Consider hollow models for large prints to save material")
