"""
Export module.
Handles saving the generated procedural planet data into files (e.g., .png, .obj).
"""

import json
import os

import numpy as np
from core.logger import get_logger

logger = get_logger(__name__)


def export_to_png(
    filepath: str,
    vertices: np.ndarray,
    faces: np.ndarray,
    heightmap: np.ndarray,
    biome_map: np.ndarray = None,
):
    """
    Exports the planet data as a 2D Equirectangular map image.

    Args:
        filepath (str): The output file path.
        vertices (numpy.ndarray): The base 3D coordinates.
        heightmap (numpy.ndarray): The elevation data.
        biome_map (numpy.ndarray, optional): The biome data for coloring.
    """
    logger.info(f"Exporting planet to PNG image: {filepath}")

    try:
        from PIL import Image, ImageDraw
    except ImportError:
        logger.error(
            "Pillow (PIL) is not installed. Cannot export PNG. "
            "Please run: pip install Pillow"
        )
        return

    width, img_height = 1024, 512
    img = Image.new("RGB", (width, img_height), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    if vertices is not None and faces is not None:
        # Extract coordinates
        x = vertices[:, 0]
        y = vertices[:, 1]
        z = vertices[:, 2]

        # Convert to spherical coordinates (longitude and latitude)
        lon = np.arctan2(z, x)
        lat = np.arcsin(np.clip(y, -1.0, 1.0))

        # Map to 2D image pixels
        px = ((lon + np.pi) / (2 * np.pi) * (width - 1)).astype(np.int32)
        py = ((lat + np.pi / 2) / np.pi * (img_height - 1)).astype(np.int32)
        py = img_height - 1 - py  # Invert Y so North is up

        # Placeholder colors (until biome_map logic is ready)
        colors = np.zeros((vertices.shape[0], 3), dtype=np.uint8)
        if heightmap is not None:
            colors[heightmap > 0.5] = [255, 255, 255]  # Snow
            colors[(heightmap <= 0.5) & (heightmap > 0.0)] = [34, 139, 34]  # Land
            colors[heightmap <= 0.0] = [0, 105, 148]  # Ocean
        else:
            colors[:] = [128, 128, 128]

        for i in range(faces.shape[0]):
            v1, v2, v3 = faces[i]

            # Check for wrap-around across the dateline (antimeridian)
            dx1 = abs(px[v1] - px[v2])
            dx2 = abs(px[v2] - px[v3])
            dx3 = abs(px[v3] - px[v1])
            if dx1 > width / 2 or dx2 > width / 2 or dx3 > width / 2:
                continue

            # Average color or color of first vertex
            c = tuple(colors[v1].tolist())
            draw.polygon([(px[v1], py[v1]), (px[v2], py[v2]), (px[v3], py[v3])], fill=c)

    img.save(filepath)
    logger.info("PNG export complete.")


def export_to_obj(
    filepath: str, vertices: np.ndarray, faces: np.ndarray, heightmap: np.ndarray
):
    """
    Exports the planet geometry as a 3D .obj file.

    Args:
        filepath (str): The output file path.
        vertices (numpy.ndarray): The base 3D coordinates of the vertices (shape N x 3).
        faces (numpy.ndarray): The triangular faces connecting the vertices (shape F x 3).
        heightmap (numpy.ndarray): The elevation data to displace the vertices.
    """
    logger.info(f"Exporting planet to OBJ 3D model: {filepath}")

    try:
        with open(filepath, "w") as f:
            f.write("# Procedural Planet Generator OBJ Export\n")

            # Write vertices
            # Assuming base radius is 1.0, we displace it by the heightmap
            for i in range(vertices.shape[0]):
                # Displacement scale (exaggerated for visibility)
                h = heightmap[i] if heightmap is not None else 0.0
                scale = 1.0 + (h * 0.1)

                x = vertices[i, 0] * scale
                y = vertices[i, 1] * scale
                z = vertices[i, 2] * scale

                f.write(f"v {x:.6f} {y:.6f} {z:.6f}\n")

            # Write faces (OBJ indices are 1-based)
            if faces is not None:
                for i in range(faces.shape[0]):
                    f.write(
                        f"f {int(faces[i, 0]) + 1} {int(faces[i, 1]) + 1} {int(faces[i, 2]) + 1}\n"
                    )

        logger.info("OBJ export complete.")

    except Exception as e:
        logger.error(f"Failed to export OBJ: {e}")
        raise


def export_to_json(
    filepath: str,
    vertices: np.ndarray,
    faces: np.ndarray,
    heightmap: np.ndarray,
    biome_map: np.ndarray = None,
):
    """
    Exports the planet geometry and biomes to a JSON file for the Web GUI.
    Matches the exact Three.js BufferGeometry specification (flat arrays).
    """
    logger.info(f"Exporting planet to JSON: {filepath}")

    flat_vertices = []
    flat_indices = []
    flat_colors = []

    if vertices is not None:
        for i in range(vertices.shape[0]):
            h = heightmap[i] if heightmap is not None else 0.0
            scale = 1.0 + (h * 0.1)

            # Displace vertex and add to flat array
            flat_vertices.extend(
                [
                    float(vertices[i, 0] * scale),
                    float(vertices[i, 1] * scale),
                    float(vertices[i, 2] * scale),
                ]
            )

            # Placeholder color logic based on height (since biome_map structure is pending)
            if h > 0.5:
                flat_colors.extend([255, 255, 255])  # Snow
            elif h > 0.0:
                flat_colors.extend([34, 139, 34])  # Land/Forest
            else:
                flat_colors.extend([0, 105, 148])  # Water

    if faces is not None:
        for i in range(faces.shape[0]):
            # Add flat indices
            flat_indices.extend([int(faces[i, 0]), int(faces[i, 1]), int(faces[i, 2])])

    data = {
        "vertices": flat_vertices,
        "indices": flat_indices,
        "colors": flat_colors,
    }

    with open(filepath, "w") as f:
        json.dump(data, f)

    logger.info("JSON export complete.")


def export_planet(planet_data: dict, filepath: str, fmt: str = "png"):
    """
    Main export router. Evaluates the requested format and calls the
    appropriate export function.

    Args:
        planet_data (dict): The generated data dictionary from PlanetGenerator.
        filepath (str): Output file path.
        fmt (str): Output format ('png', 'obj', or 'json').
    """
    heightmap = planet_data.get("heightmap")
    vertices = planet_data.get("vertices")
    faces = planet_data.get("faces")
    biome_map = planet_data.get("biome_map")

    fmt = fmt.lower()

    if fmt == "obj":
        if not filepath.endswith(".obj"):
            filepath += ".obj"
        export_to_obj(filepath, vertices, faces, heightmap)
    elif fmt == "json":
        if not filepath.endswith(".json"):
            filepath += ".json"
        export_to_json(filepath, vertices, faces, heightmap, biome_map)
    else:
        if not filepath.endswith(".png"):
            filepath += ".png"
        export_to_png(filepath, vertices, faces, heightmap, biome_map)
