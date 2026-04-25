"""
Optimized data types and core structures.
Contains Numba-optimized functions and data structures required for
fast, real-time procedural generation.
"""

import numpy as np
from numba import njit, prange


def create_vector3_array(size):
    """
    Creates a highly optimized NumPy array tailored for storing 3D vectors
    (e.g., coordinates, normals) compatible with Numba JIT compilation.

    Args:
        size (int): The number of 3D vectors to allocate.

    Returns:
        numpy.ndarray: An array of shape (size, 3) optimized for math operations.
    """
    # Using float32 for faster calculations and lower memory footprint
    return np.zeros((size, 3), dtype=np.float32)


@njit(parallel=True, fastmath=True)
def normalize_vectors_fast(vectors):
    """
    A fast, Numba-optimized function to normalize an array of 3D vectors.
    Essential for projecting points onto a spherical surface.

    Args:
        vectors (numpy.ndarray): An array of 3D vectors to normalize.

    Returns:
        numpy.ndarray: An array of normalized 3D vectors.
    """
    result = np.empty_like(vectors)
    for i in prange(vectors.shape[0]):
        x = vectors[i, 0]
        y = vectors[i, 1]
        z = vectors[i, 2]
        length = np.sqrt(x * x + y * y + z * z)

        if length > 0:
            result[i, 0] = x / length
            result[i, 1] = y / length
            result[i, 2] = z / length
        else:
            result[i, 0] = 0.0
            result[i, 1] = 0.0
            result[i, 2] = 0.0

    return result


def create_spherical_grid(resolution):
    """
    Allocates a contiguous block of memory for the spherical planet grid,
    suitable for fast, cache-friendly reads and writes during cellular automata
    simulations and heightmap generation.

    Args:
        resolution (int): The base resolution or subdivision level of the grid.

    Returns:
        numpy.ndarray: The allocated data structure representing the grid cells.
    """
    # Placeholder formula for array size based on resolution.
    # We allocate it as a contiguous float32 2D array.
    total_points = resolution * resolution
    return create_vector3_array(total_points)


@njit(fastmath=True)
def fast_distance_3d(point_a, point_b):
    """
    A Numba-optimized helper function to quickly calculate the Euclidean
    distance between two points in 3D space.

    Args:
        point_a (tuple or numpy.ndarray): Coordinates of the first point (x, y, z).
        point_b (tuple or numpy.ndarray): Coordinates of the second point (x, y, z).

    Returns:
        float: The calculated Euclidean distance.
    """
    dx = point_a[0] - point_b[0]
    dy = point_a[1] - point_b[1]
    dz = point_a[2] - point_b[2]
    return np.sqrt(dx * dx + dy * dy + dz * dz)
