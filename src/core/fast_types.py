"""
Optimized data types and core structures.
Contains Numba-optimized functions and data structures required for
fast, real-time procedural generation.
"""


def create_vector3_array(size):
    """
    Creates a highly optimized NumPy array tailored for storing 3D vectors
    (e.g., coordinates, normals) compatible with Numba JIT compilation.

    Args:
        size (int): The number of 3D vectors to allocate.

    Returns:
        numpy.ndarray: An array of shape (size, 3) optimized for math operations.
    """
    pass


def normalize_vectors_fast(vectors):
    """
    A fast, Numba-optimized function to normalize an array of 3D vectors.
    Essential for projecting points onto a spherical surface.

    Args:
        vectors (numpy.ndarray): An array of 3D vectors to normalize.

    Returns:
        numpy.ndarray: An array of normalized 3D vectors.
    """
    pass


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
    pass


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
    pass
