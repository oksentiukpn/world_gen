"""
Climate and biome generation.
Handles temperature and moisture calculations based on terrain height
and latitude, and determines the resulting biomes for the 3D Icosphere.

INSTRUCTIONS FOR PARTICIPANT 2 (LOGIC / BIOMES):
-----------------------------------------------------------
1. The planet is a 3D sphere, not a 2D map!
2. To find the "latitude" (equator vs poles) of a point, look at its `y` coordinate
   in the `vertices` array. Since the sphere is normalized, `y` ranges from
   -1.0 (South Pole) to 0.0 (Equator) to 1.0 (North Pole).
3. Temperature should be highest at y=0 and lowest at y=1 or y=-1.
   Remember: Temperature also decreases as height (elevation) increases (mountains are cold).
4. Determine biomes using a Whittaker diagram approach (Temperature vs Moisture).
5. Use Numba! Wrap your math-heavy functions in @njit(fastmath=True)
   to ensure they run instantly for hundreds of thousands of vertices.
"""

import numpy as np
from numba import njit, prange


# @njit(fastmath=True) # Uncomment when implementing
def calculate_temperature(y_coord, elevation):
    """
    Calculates the temperature of a specific vertex based on its latitude (y_coord)
    and its elevation (height).

    Args:
        y_coord (float): The normalized y-coordinate (-1.0 to 1.0).
        elevation (float): The terrain height at this vertex.

    Returns:
        float: The calculated temperature value (e.g., 0.0 to 1.0).
    """
    # TODO (Participant 2):
    # 1. Calculate base temp from latitude (abs(y_coord)). Equator is hot, poles are cold.
    # 2. Subtract temperature based on elevation (higher = colder).
    return 0.5


# @njit(fastmath=True)
def calculate_moisture(elevation):
    """
    Calculates the moisture level of a specific vertex.

    Args:
        elevation (float): The terrain height at this vertex.

    Returns:
        float: The calculated moisture value.
    """
    # TODO (Participant 2):
    # 1. Base moisture can depend on proximity to ocean (elevation <= 0).
    # 2. Advanced: simulate rain shadows based on wind direction and mountains.
    return 0.5


# @njit(fastmath=True)
def determine_biome(temperature, moisture):
    """
    Determines the biome category based on temperature and moisture levels.

    Args:
        temperature (float): The calculated temperature at the location.
        moisture (float): The calculated moisture at the location.

    Returns:
        int: An identifier/code for the resulting biome.
    """
    # TODO (Participant 2):
    # Map (temperature, moisture) pairs to biome IDs.
    # e.g., 0 = Ocean, 1 = Desert, 2 = Forest, 3 = Snow
    return 0


# @njit(parallel=True, fastmath=True)
def generate_biome_map(heightmap, vertices):
    """
    Orchestrates the generation of a full biome map for all vertices.
    Calculates temperature and moisture for each vertex and assigns a biome.

    Args:
        heightmap (numpy.ndarray): 1D array of terrain elevations.
        vertices (numpy.ndarray): 2D array of normalized vertex coordinates (V x 3).

    Returns:
        numpy.ndarray: A 1D array containing the resulting biome ID for each vertex.
    """
    num_vertices = heightmap.shape[0]
    biome_map = np.zeros(num_vertices, dtype=np.int32)

    # TODO (Participant 2):
    # 1. Use a loop (prange) to iterate over all vertices.
    # 2. For each vertex `i`:
    #    - Get `y` from vertices[i, 1]
    #    - Get `elevation` from heightmap[i]
    #    - temp = calculate_temperature(...)
    #    - moist = calculate_moisture(...)
    #    - biome_map[i] = determine_biome(temp, moist)

    return biome_map
