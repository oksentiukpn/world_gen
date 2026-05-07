import os

import numpy as np
from PIL import Image
from src.core.config import ExportConfig
from src.core.export.png_exporter import PngExporter
from src.core.planet_data import PlanetData


def test_png_exporter(tmpdir):
    exporter = PngExporter()
    # Provide points roughly in front
    vertices = np.array([[1.0, 0.0, 0.0], [0.8, 0.5, 0.0], [0.8, -0.5, 0.0]])
    faces = np.array([[0, 1, 2]])
    heightmap = np.array([0.0, 0.0, 0.0])
    biome_map = np.array([[255, 0, 0], [0, 255, 0], [0, 0, 255]], dtype=np.uint8)

    data = PlanetData(
        vertices=vertices,
        faces=faces,
        heightmap=heightmap,
        biome_map=biome_map,
        radius=1.0,
    )
    config = ExportConfig(output_path=str(tmpdir.join("test")))

    exporter.export(data, config)

    output_file = str(tmpdir.join("test.png"))
    assert os.path.exists(output_file)

    img = Image.open(output_file)
    assert img.size == (1024, 512)
    assert img.mode == "RGB"


def test_png_exporter_cross_antimeridian(tmpdir):
    exporter = PngExporter()
    # Provide points that cross the antimeridian
    vertices = np.array([[-1.0, 0.0, 0.1], [-1.0, 0.5, -0.1], [-1.0, -0.5, 0.1]])
    faces = np.array([[0, 1, 2]])
    heightmap = np.array([0.0, 0.0, 0.0])
    biome_map = np.array([[255, 0, 0], [0, 255, 0], [0, 0, 255]], dtype=np.uint8)

    data = PlanetData(
        vertices=vertices,
        faces=faces,
        heightmap=heightmap,
        biome_map=biome_map,
        radius=1.0,
    )
    config = ExportConfig(output_path=str(tmpdir.join("test_anti")))

    exporter.export(data, config)

    output_file = str(tmpdir.join("test_anti.png"))
    assert os.path.exists(output_file)
