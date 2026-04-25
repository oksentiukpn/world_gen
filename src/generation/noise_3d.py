"""
3D Noise generation algorithms.
Contains functions for generating fractal noise (e.g., Simplex, Perlin)
on a spherical surface to create realistic heightmaps.
"""

import math

import numpy as np
from numba import njit, prange


@njit(fastmath=True)
def pcg_hash(x, y, z, seed=0):
    # 32-bit
    mask = 0xFFFFFFFF

    state = (x * 1664525 + y * 1013904223 + z * 214013 + seed * 735044629) & mask

    word = ((state >> ((state >> 28) + 4)) ^ state) * 277803737
    word &= mask

    return (word >> 22) ^ word


@njit(fastmath=True)
def hash_vector(x, y, z, seed=0):
    hash_x = pcg_hash(x, y, z, seed)
    hash_y = pcg_hash(x + 12345, y + 67890, z + 13579, seed)

    # [-pi / 2, pi / 2]
    theta = math.acos((hash_x / 0xFFFFFFFF) * 2 - 1)
    # [0, 2 * pi]
    phi = 2.0 * math.pi * (hash_y / 0xFFFFFFFF)

    vector_x = math.cos(phi) * math.sin(theta)
    vector_y = math.sin(phi) * math.sin(theta)
    vector_z = math.cos(theta)

    return vector_x, vector_y, vector_z


@njit(fastmath=True)
def dot_product(
    vector1: tuple[float, float, float], vector2: tuple[float, float, float]
):
    return vector1[0] * vector2[0] + vector1[1] * vector2[1] + vector1[2] * vector2[2]


@njit(fastmath=True)
def lerp(a, b, t):
    return a + t * (b - a)


@njit(fastmath=True)
def fade(x):
    # Формула Кенна Перліна: 6t^5 - 15t^4 + 10t^3
    return x * x * x * (x * (x * 6 - 15) + 10)


@njit(fastmath=True)
def perlin_noise_3d(x, y, z, seed=0):
    """
    Generates a single octave of 3D Simplex or Perlin noise at the given coordinates.

    Args:
        x (float): The x-coordinate in 3D space.
        y (float): The y-coordinate in 3D space.
        z (float): The z-coordinate in 3D space.
        seed (int, optional): The seed for the noise permutation. Defaults to 0.

    Returns:
        float: A noise value, typically ranging from -1.0 to 1.0.
    """
    x_floor = int(math.floor(x))
    y_floor = int(math.floor(y))
    z_floor = int(math.floor(z))

    x_ceil = x_floor + 1
    y_ceil = y_floor + 1
    z_ceil = z_floor + 1

    # (((000 100) (010 110)) ((001 101)(011 111)))

    points = [
        (x_floor, y_floor, z_floor),
        (x_ceil, y_floor, z_floor),
        (x_floor, y_ceil, z_floor),
        (x_ceil, y_ceil, z_floor),
        (x_floor, y_floor, z_ceil),
        (x_ceil, y_floor, z_ceil),
        (x_floor, y_ceil, z_ceil),
        (x_ceil, y_ceil, z_ceil),
    ]

    vectors_to_coord = [(x - point[0], y - point[1], z - point[2]) for point in points]

    gradients = [hash_vector(x, y, z, seed) for x, y, z in points]

    dots = [
        dot_product(v_to_coord, grad)
        for v_to_coord, grad in zip(vectors_to_coord, gradients)
    ]  # dot_products

    value = lerp(
        lerp(
            lerp(dots[0], dots[1], fade(x - x_floor)),
            lerp(dots[2], dots[3], fade(x - x_floor)),
            fade(y - y_floor),
        ),
        lerp(
            lerp(dots[4], dots[5], fade(x - x_floor)),
            lerp(dots[6], dots[7], fade(x - x_floor)),
            fade(y - y_floor),
        ),
        fade(z - z_floor),
    )

    return value


@njit(fastmath=True)
def fractal_perlin_noise_3d(
    x, y, z, scale=0.5, octaves=4, persistence=0.5, lacunarity=2.0, seed=0
):
    """
    Generates fractal terrain noise using Fractional Brownian Motion (fBm)
    by layering multiple octaves of 3D noise.

    Args:
        x (float): The x-coordinate in 3D space.
        y (float): The y-coordinate in 3D space.
        z (float): The z-coordinate in 3D space.
        octaves (int, optional): The number of noise layers. Defaults to 4.
        persistence (float, optional): The amplitude multiplier per octave. Defaults to 0.5.
        lacunarity (float, optional): The frequency multiplier per octave. Defaults to 2.0.
        seed (int, optional): The noise seed. Defaults to 0.

    Returns:
        float: The combined fractal noise value.
    """
    amplitude = 1
    curr_scale = scale
    value = 0
    for i in range(octaves):
        octave_seed = seed + i * 1337
        value += (
            perlin_noise_3d(x * curr_scale, y * curr_scale, z * curr_scale, octave_seed)
            * amplitude
        )
        amplitude *= persistence
        curr_scale *= lacunarity

    return value


@njit(fastmath=True)
def apply_ridge_noise(x, y, z, octaves=4, persistence=0.5, lacunarity=2.0, seed=0):
    """
    Generates rigid/ridged multi-fractal noise, which is ideal for creating
    sharp mountain peaks and steep valleys.

    Args:
        x (float): The x-coordinate in 3D space.
        y (float): The y-coordinate in 3D space.
        z (float): The z-coordinate in 3D space.
        octaves (int, optional): The number of noise layers. Defaults to 4.
        persistence (float, optional): The amplitude multiplier per octave. Defaults to 0.5.
        lacunarity (float, optional): The frequency multiplier per octave. Defaults to 2.0.
        seed (int, optional): The noise seed. Defaults to 0.

    Returns:
        float: The computed ridged noise value.
    """
    pass


@njit(parallel=True, fastmath=True)
def generate_heightmap(grid_points, seed=0):
    """
    Generates a complete heightmap for a sphere by evaluating 3D noise
    at each normalized coordinate on the spherical grid.

    Args:
        grid_points (numpy.ndarray): An array of 3D vectors representing points on the sphere.
        seed (int, optional): The master seed for planetary generation. Defaults to 0.

    Returns:
        numpy.ndarray: An array of elevation values corresponding to each grid point.
    """

    n_points = grid_points.shape[0]
    elevations = np.empty(n_points, dtype=np.float32)

    for i in prange(n_points):
        elevations[i] = fractal_perlin_noise_3d(
            grid_points[i, 0],
            grid_points[i, 1],
            grid_points[i, 2],
            scale=0.5,
            octaves=4,
            persistence=0.5,
            lacunarity=2.0,
            seed=seed,
        )

    return elevations
