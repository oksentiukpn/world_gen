"""
Export module.
Handles saving the generated procedural planet data into files (e.g., .png, .obj).
"""

import os

import numpy as np
from core.logger import get_logger

logger = get_logger(__name__)


def export_to_png(filepath: str, heightmap: np.ndarray, biome_map: np.ndarray = None):
    """
    Exports the planet data as a 2D image (e.g., Equirectangular projection).

    Args:
        filepath (str): The output file path.
        heightmap (numpy.ndarray): The elevation data.
        biome_map (numpy.ndarray, optional): The biome data for coloring.
    """
    logger.info(f"Exporting planet to PNG image: {filepath}")

    # Placeholder for actual image generation logic (e.g., using PIL or Matplotlib)
    # Note: Since the grid is spherical, this requires projecting the 3D points
    # onto a 2D equirectangular grid before saving as an image.
    logger.warning("PNG export logic is currently a placeholder.")

    # Simulated file creation for pipeline testing
    with open(filepath, "w") as f:
        f.write("PNG EXPORT PLACEHOLDER\n")

    logger.info("PNG export complete.")


def export_to_obj(filepath: str, grid_points: np.ndarray, heightmap: np.ndarray):
    """
    Exports the planet geometry as a 3D .obj file.

    Args:
        filepath (str): The output file path.
        grid_points (numpy.ndarray): The base 3D coordinates of the grid (shape N x 3).
        heightmap (numpy.ndarray): The elevation data to displace the vertices.
    """
    logger.info(f"Exporting planet to OBJ 3D model: {filepath}")

    try:
        with open(filepath, "w") as f:
            f.write("# Procedural Planet Generator OBJ Export\n")

            # Write vertices
            # Assuming base radius is 1.0, we displace it by the heightmap
            for i in range(grid_points.shape[0]):
                # Displacement scale (exaggerated for visibility)
                h = heightmap[i] if heightmap is not None else 0.0
                scale = 1.0 + (h * 0.1)

                x = grid_points[i, 0] * scale
                y = grid_points[i, 1] * scale
                z = grid_points[i, 2] * scale

                f.write(f"v {x:.6f} {y:.6f} {z:.6f}\n")

            # Note: Writing faces (f v1 v2 v3) requires knowledge of the grid topology
            # (e.g., an icosphere index buffer). For now, we export a point cloud.
            logger.warning(
                "OBJ export currently outputs a point cloud (vertices only) until topology indexing is implemented."
            )

        logger.info("OBJ export complete.")

    except Exception as e:
        logger.error(f"Failed to export OBJ: {e}")
        raise


def export_planet(planet_data: dict, filepath: str, fmt: str = "png"):
    """
    Main export router. Evaluates the requested format and calls the
    appropriate export function.

    Args:
        planet_data (dict): The generated data dictionary from PlanetGenerator.
        filepath (str): Output file path.
        fmt (str): Output format ('png' or 'obj').
    """
    heightmap = planet_data.get("heightmap")
    grid = planet_data.get("grid")
    biome_map = planet_data.get("biome_map")

    if fmt.lower() == "obj":
        if not filepath.endswith(".obj"):
            filepath += ".obj"
        export_to_obj(filepath, grid, heightmap)
    else:
        if not filepath.endswith(".png"):
            filepath += ".png"
        export_to_png(filepath, heightmap, biome_map)
