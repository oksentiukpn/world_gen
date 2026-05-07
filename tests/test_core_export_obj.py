import os

import numpy as np
from src.core.config import ExportConfig
from src.core.export.base import TERRAIN_DISPLACEMENT_SCALE
from src.core.export.obj_exporter import ObjExporter
from src.core.planet_data import PlanetData


def test_obj_exporter(tmpdir):
    exporter = ObjExporter()
    vertices = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    faces = np.array([[0, 1, 2]])
    heightmap = np.array([0.0, 1.0, -1.0])
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

    output_file = str(tmpdir.join("test.obj"))
    assert os.path.exists(output_file)

    with open(output_file, "r") as f:
        lines = f.readlines()

    assert lines[0] == "# Procedural Planet Generator — OBJ Export\n"

    expected_v1_dist = 1.0 + TERRAIN_DISPLACEMENT_SCALE
    expected_v2_dist = 1.0 - TERRAIN_DISPLACEMENT_SCALE

    assert lines[1] == "v 1.000000 0.000000 0.000000 1.000 0.000 0.000\n"
    assert lines[2] == f"v 0.000000 {expected_v1_dist:.6f} 0.000000 0.000 1.000 0.000\n"
    assert lines[3] == f"v 0.000000 0.000000 {expected_v2_dist:.6f} 0.000 0.000 1.000\n"
    assert lines[4] == "f 1 2 3\n"
