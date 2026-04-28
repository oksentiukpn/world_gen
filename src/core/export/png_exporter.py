"""
PNG exporter — equirectangular 2D projection of the planet surface.

radius and terrain_scale have no effect here: the projection is purely
angle-based so uniform scaling does not change the output image.
"""

import numpy as np
from core.config import ExportConfig
from core.export.base import BaseExporter, ensure_extension, get_color
from core.planet_data import PlanetData


class PngExporter(BaseExporter):
    """Exports the planet as a 2D equirectangular PNG image."""

    WIDTH = 1024
    HEIGHT = 512

    def export(self, data: PlanetData, config: ExportConfig) -> None:
        filepath = ensure_extension(config.output_path, ".png")
        self.logger.info(f"Exporting planet to PNG: {filepath}")

        try:
            from PIL import Image, ImageDraw
        except ImportError:
            self.logger.error("Pillow is not installed. Run: pip install Pillow")
            return

        img = Image.new("RGB", (self.WIDTH, self.HEIGHT), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        if data.vertices is not None and data.faces is not None:
            px, py = self._project(data.vertices)

            for i in range(data.faces.shape[0]):
                v1, v2, v3 = data.faces[i]

                # Skip faces that cross the antimeridian
                if (
                    abs(px[v1] - px[v2]) > self.WIDTH // 2
                    or abs(px[v2] - px[v3]) > self.WIDTH // 2
                    or abs(px[v3] - px[v1]) > self.WIDTH // 2
                ):
                    continue

                c = get_color(data.biome_map, v1)
                draw.polygon(
                    [(px[v1], py[v1]), (px[v2], py[v2]), (px[v3], py[v3])],
                    fill=c,
                )

        img.save(filepath)
        self.logger.info("PNG export complete.")

    def _project(self, vertices: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """Converts 3D unit-sphere vertices to equirectangular pixel coordinates."""
        x, y, z = vertices[:, 0], vertices[:, 1], vertices[:, 2]

        lon = np.arctan2(z, x)
        lat = np.arcsin(np.clip(y, -1.0, 1.0))

        px = ((lon + np.pi) / (2 * np.pi) * (self.WIDTH - 1)).astype(np.int32)
        py = ((lat + np.pi / 2) / np.pi * (self.HEIGHT - 1)).astype(np.int32)
        py = self.HEIGHT - 1 - py  # north-up

        return px, py
