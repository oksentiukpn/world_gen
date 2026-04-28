"""
PlanetData dataclass.

Typed container for all arrays produced by the generation pipeline.
Replaces the untyped dict that PlanetGenerator.generate() previously returned.
"""

from dataclasses import dataclass

import numpy as np


@dataclass
class PlanetData:
    """
    All data produced by a single run of the generation pipeline.

    Attributes:
        vertices (np.ndarray): Normalized 3D coordinates of icosphere vertices,
                               shape (V, 3), dtype float32.
        faces (np.ndarray): Triangular face indices into `vertices`,
                            shape (F, 3), dtype int32.
        heightmap (np.ndarray): Scalar elevation value per vertex,
                                shape (V,), dtype float32.
        biome_map (np.ndarray): Per-vertex biome data produced by biome/climate.py.
                                Shape (V, 3) uint8 RGB once implemented;
                                shape (V,) int32 zeros until then.
    """

    vertices: np.ndarray
    faces: np.ndarray
    heightmap: np.ndarray
    biome_map: np.ndarray
