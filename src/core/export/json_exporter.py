"""
JSON exporter — Three.js BufferGeometry flat-array format for the Web GUI.

Vertex position formula:
    final_pos = vertex_normalized * (radius + h * TERRAIN_DISPLACEMENT_SCALE)

radius comes from PlanetData (set at generation time via PlanetConfig).
TERRAIN_DISPLACEMENT_SCALE is a fixed internal constant.
"""

import json

from core.config import ExportConfig
from core.export.base import (
    TERRAIN_DISPLACEMENT_SCALE,
    BaseExporter,
    ensure_extension,
    get_color,
)
from core.planet_data import PlanetData


class JsonExporter(BaseExporter):
    """
    Exports planet geometry and biome colors to JSON.
    Output matches the Three.js BufferGeometry flat-array specification.
    """

    def export(self, data: PlanetData, config: ExportConfig) -> None:
        filepath = ensure_extension(config.output_path, ".json")
        self.logger.info(f"Exporting planet to JSON: {filepath}")

        flat_vertices: list[float] = []
        flat_colors: list[int] = []

        if data.vertices is not None:
            for i in range(data.vertices.shape[0]):
                h = float(data.heightmap[i]) if data.heightmap is not None else 0.0
                dist = data.radius + h * TERRAIN_DISPLACEMENT_SCALE

                flat_vertices.extend(
                    [
                        float(data.vertices[i, 0] * dist),
                        float(data.vertices[i, 1] * dist),
                        float(data.vertices[i, 2] * dist),
                    ]
                )
                flat_colors.extend(get_color(data.biome_map, i))

        flat_indices: list[int] = (
            data.faces.flatten().tolist() if data.faces is not None else []
        )

        payload = {
            "vertices": flat_vertices,
            "indices": flat_indices,
            "colors": flat_colors,
        }

        with open(filepath, "w") as f:
            json.dump(payload, f)

        self.logger.info("JSON export complete.")
