"""
Base exporter interface and shared utilities.

Every format-specific exporter inherits from BaseExporter and implements
a single method: export(data, config).
"""

from abc import ABC, abstractmethod

import numpy as np
from core.config import ExportConfig
from core.logger import get_logger
from core.planet_data import PlanetData

FALLBACK_COLOR: tuple[int, int, int] = (128, 128, 128)


def get_color(biome_map: np.ndarray | None, index: int) -> tuple[int, int, int]:
    """
    Returns the RGB color for a vertex by looking it up in biome_map.
    Falls back to neutral grey if biome_map is absent or not yet implemented.

    Args:
        biome_map: Array of shape (V, 3) uint8 RGB per vertex produced by
                   biome/climate.py. A 1D array is treated as a stub (not ready).
        index: Vertex index.

    Returns:
        RGB tuple with values in 0-255.
    """
    if biome_map is not None and biome_map.ndim == 2 and biome_map.shape[1] == 3:
        return (
            int(biome_map[index, 0]),
            int(biome_map[index, 1]),
            int(biome_map[index, 2]),
        )
    return FALLBACK_COLOR


def ensure_extension(path: str, ext: str) -> str:
    """Returns path unchanged if it already ends with ext, otherwise appends it."""
    return path if path.endswith(ext) else path + ext


class BaseExporter(ABC):
    """
    Abstract base class for all planet exporters.

    To add a new export format:
      1. Create a subclass of BaseExporter in its own module.
      2. Implement export().
      3. Register the class in core/export/__init__.py.
    """

    def __init__(self) -> None:
        self.logger = get_logger(
            f"{self.__class__.__module__}.{self.__class__.__name__}"
        )

    @abstractmethod
    def export(self, data: PlanetData, config: ExportConfig) -> None:
        """
        Serializes planet data to disk in this exporter's format.

        Args:
            data:   Generated planet geometry and biome data.
            config: Output path, radius, terrain_scale, etc.
        """
        ...
