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

BLUE = (52, 140, 206)
BLUE_GREY = (182, 199, 204)
DARK_GREEN = (60, 100, 85)
MEDIUM_GREEN = (85, 150, 95)
PALE_SAND = (232, 200, 138)
LIGHT_GREEN = (152, 200, 115)
GOLDEN_BROWN = (210, 180, 115)
WHITE = (245, 250, 255)
GREY = (145, 150, 155)


@njit(fastmath=True)
def calculate_temperature(y_coord, elevation):
    """
    Calculates temperature in degrees Celsius (approx -20 to 30).
    Equator = 30°C, Poles = -20°C. Elevation reduces temperature.
    """
    dist_from_equator = abs(y_coord)

    base_temp = 30.0 - (dist_from_equator * 50.0)

    elevation_penalty = elevation * 20.0

    return base_temp - elevation_penalty


@njit(fastmath=True)
def calculate_moisture(elevation):
    """
    Calculates humidity/moisture in cm (0 to 400+).
    Maps the normalized elevation levels to your required humidity thresholds.
    """
    return 450 * (1 - elevation)


@njit(fastmath=True)
def determine_color(temperature, humidity, elevation):
    """
    Determines the biome category using the simplified Whittaker classification.
    Incorporates priority overrides for Ocean, Snow, and High Peaks.

    IDs: 0=Ocean, 1=Tundra, 2=Taiga, 3=Temperate Forest, 4=Desert,
         5=Grassland, 6=Savanna, 7=Rainforest, 8=Snow, 9=Rock
    """

    if elevation <= 0:
        return BLUE

    if temperature < -5:
        if temperature < -10:
            return WHITE
        return BLUE_GREY

    elif temperature < 20:
        if humidity <= 220:
            return DARK_GREEN
        if humidity <= 350:
            return MEDIUM_GREEN
        else:
            return LIGHT_GREEN

    else:
        if humidity <= 400:
            return GOLDEN_BROWN
        else:
            return PALE_SAND


@njit(parallel=True, fastmath=True)
def generate_biome_map(heightmap, vertices):
    """
    Orchestrates the generation of a full biome map for all vertices.
    Normalizes the heightmap dynamically so arbitrary elevation ranges work perfectly.
    """
    num_vertices = heightmap.shape[0]
    biome_map = np.zeros((num_vertices, 3), dtype=np.uint8)

    min_elevation = np.min(heightmap)
    max_elevation = np.max(heightmap)
    elevation_range = max_elevation - min_elevation

    if elevation_range == 0.0:
        elevation_range = 1.0

    for i in prange(num_vertices):
        y_coord = vertices[i, 1]

        # Normalize the current elevation to a 0.0 -> 1.0 scale
        raw_elevation = heightmap[i]
        normalized_elevation = (raw_elevation - min_elevation) / elevation_range

        temp = calculate_temperature(y_coord, normalized_elevation)
        moist = calculate_moisture(normalized_elevation)

        r, g, b = determine_color(temp, moist, normalized_elevation)
        biome_map[i, 0] = r
        biome_map[i, 1] = g
        biome_map[i, 2] = b

    return biome_map
