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


def create_faces_array(size):
    """
    Creates a highly optimized NumPy array tailored for storing 3D triangular faces
    (indices of vertices).

    Args:
        size (int): The number of triangular faces to allocate.

    Returns:
        numpy.ndarray: An array of shape (size, 3) optimized for indexing operations.
    """
    return np.zeros((size, 3), dtype=np.int32)


def create_spherical_grid(subdivisions):
    """
    Generates an Icosphere by recursively subdividing a base icosahedron.

    Args:
        subdivisions (int): The subdivision level of the base icosahedron.

    Returns:
        tuple[numpy.ndarray, numpy.ndarray]: A tuple containing:
            - vertices: An array of normalized 3D coordinates (shape: V x 3).
            - faces: An array of vertex indices forming triangles (shape: F x 3).
    """
    t = (1.0 + np.sqrt(5.0)) / 2.0

    vertices = [
        [-1, t, 0],
        [1, t, 0],
        [-1, -t, 0],
        [1, -t, 0],
        [0, -1, t],
        [0, 1, t],
        [0, -1, -t],
        [0, 1, -t],
        [t, 0, -1],
        [t, 0, 1],
        [-t, 0, -1],
        [-t, 0, 1],
    ]

    faces = [
        [0, 11, 5],
        [0, 5, 1],
        [0, 1, 7],
        [0, 7, 10],
        [0, 10, 11],
        [1, 5, 9],
        [5, 11, 4],
        [11, 10, 2],
        [10, 7, 6],
        [7, 1, 8],
        [3, 9, 4],
        [3, 4, 2],
        [3, 2, 6],
        [3, 6, 8],
        [3, 8, 9],
        [4, 9, 5],
        [2, 4, 11],
        [6, 2, 10],
        [8, 6, 7],
        [9, 8, 1],
    ]

    midpoint_cache = {}

    def get_midpoint(v1, v2):
        key = (min(v1, v2), max(v1, v2))
        if key in midpoint_cache:
            return midpoint_cache[key]

        p1 = vertices[v1]
        p2 = vertices[v2]
        pmid = [
            (p1[0] + p2[0]) / 2.0,
            (p1[1] + p2[1]) / 2.0,
            (p1[2] + p2[2]) / 2.0,
        ]
        idx = len(vertices)
        vertices.append(pmid)
        midpoint_cache[key] = idx
        return idx

    for _ in range(subdivisions):
        new_faces = []
        for tri in faces:
            v1, v2, v3 = tri
            a = get_midpoint(v1, v2)
            b = get_midpoint(v2, v3)
            c = get_midpoint(v3, v1)

            new_faces.append([v1, a, c])
            new_faces.append([v2, b, a])
            new_faces.append([v3, c, b])
            new_faces.append([a, b, c])
        faces = new_faces

    vertices_np = np.array(vertices, dtype=np.float32)
    faces_np = np.array(faces, dtype=np.int32)

    # Normalize vertices to push them to the sphere surface
    vertices_np = normalize_vectors_fast(vertices_np)

    return vertices_np, faces_np


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


@njit(fastmath=True)
def build_adjacency_list(num_vertices, faces):
    """
    Builds a Numba-optimized adjacency list for the icosphere graph.
    Vertices on an icosphere have at most 6 neighbors (base vertices have 5).

    Args:
        num_vertices (int): Total number of vertices.
        faces (numpy.ndarray): The triangular faces array.

    Returns:
        numpy.ndarray: An array of shape (V, 6) containing neighbor indices.
                       Unused slots (for base vertices with 5 neighbors) are -1.
    """
    adj = np.full((num_vertices, 6), -1, dtype=np.int32)
    counts = np.zeros(num_vertices, dtype=np.int32)

    for i in range(faces.shape[0]):
        for j in range(3):
            a = faces[i, j]
            b = faces[i, (j + 1) % 3]

            # Add b to a's neighbors
            found = False
            for k in range(counts[a]):
                if adj[a, k] == b:
                    found = True
                    break
            if not found:
                adj[a, counts[a]] = b
                counts[a] += 1

            # Add a to b's neighbors
            found = False
            for k in range(counts[b]):
                if adj[b, k] == a:
                    found = True
                    break
            if not found:
                adj[b, counts[b]] = a
                counts[b] += 1

    return adj
