"""
OBJ exporter — Wavefront .obj 3D mesh with per-vertex RGB colors.

Vertex position formula:
    final_pos = vertex_normalized * (radius + h * TERRAIN_DISPLACEMENT_SCALE)

radius comes from PlanetData (set at generation time via PlanetConfig).
TERRAIN_DISPLACEMENT_SCALE is a fixed internal constant.
"""

from core.config import ExportConfig
from core.export.base import (
    TERRAIN_DISPLACEMENT_SCALE,
    BaseExporter,
    ensure_extension,
    get_color,
)
from core.planet_data import PlanetData


class ObjExporter(BaseExporter):
    """Exports the planet geometry as a Wavefront .obj file with per-vertex colors."""

    def export(self, data: PlanetData, config: ExportConfig) -> None:
        filepath = ensure_extension(config.output_path, ".obj")
        self.logger.info(f"Exporting planet to OBJ: {filepath}")

        try:
            with open(filepath, "w") as f:
                f.write("# Procedural Planet Generator — OBJ Export\n")
                self._write_vertices(f, data)
                self._write_faces(f, data)
        except Exception as e:
            self.logger.error(f"Failed to export OBJ: {e}")
            raise

        self.logger.info("OBJ export complete.")

    def _write_vertices(self, f, data: PlanetData) -> None:
        for i in range(data.vertices.shape[0]):
            h = float(data.heightmap[i]) if data.heightmap is not None else 0.0
            dist = data.radius + h * TERRAIN_DISPLACEMENT_SCALE

            vx = data.vertices[i, 0] * dist
            vy = data.vertices[i, 1] * dist
            vz = data.vertices[i, 2] * dist

            cr, cg, cb = get_color(data.biome_map, i)
            f.write(
                f"v {vx:.6f} {vy:.6f} {vz:.6f} "
                f"{cr / 255:.3f} {cg / 255:.3f} {cb / 255:.3f}\n"
            )

    def _write_faces(self, f, data: PlanetData) -> None:
        if data.faces is None:
            return
        for i in range(data.faces.shape[0]):
            a = int(data.faces[i, 0]) + 1
            b = int(data.faces[i, 1]) + 1
            c = int(data.faces[i, 2]) + 1
            f.write(f"f {a} {b} {c}\n")
