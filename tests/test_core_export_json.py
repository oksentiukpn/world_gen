import json
import os

import numpy as np
from src.core.config import ExportConfig
from src.core.export.base import TERRAIN_DISPLACEMENT_SCALE
from src.core.export.json_exporter import JsonExporter
from src.core.planet_data import PlanetData


def test_json_exporter(tmpdir):
    exporter = JsonExporter()
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

    output_file = str(tmpdir.join("test.json"))
    assert os.path.exists(output_file)

    with open(output_file, "r") as f:
        payload = json.load(f)

    assert "vertices" in payload
    assert "indices" in payload
    assert "colors" in payload

    assert payload["indices"] == [0, 1, 2]
    assert payload["colors"] == [255, 0, 0, 0, 255, 0, 0, 0, 255]

    # Check vertex 0: height = 0.0, radius=1.0 -> dist = 1.0. pos = (1.0, 0.0, 0.0)
    # Check vertex 1: height = 1.0, radius=1.0 -> dist = 1.0 + TERRAIN_DISPLACEMENT_SCALE. pos = (0.0, dist, 0.0)
    # Check vertex 2: height = -1.0, radius=1.0 -> dist = 1.0 - TERRAIN_DISPLACEMENT_SCALE. pos = (0.0, 0.0, dist)
    expected_v1_dist = 1.0 + TERRAIN_DISPLACEMENT_SCALE
    expected_v2_dist = 1.0 - TERRAIN_DISPLACEMENT_SCALE

    np.testing.assert_allclose(
        payload["vertices"],
        [1.0, 0.0, 0.0, 0.0, expected_v1_dist, 0.0, 0.0, 0.0, expected_v2_dist],
    )


def test_json_exporter_empty(tmpdir):
    exporter = JsonExporter()
    data = PlanetData(
        vertices=None, faces=None, heightmap=None, biome_map=None, radius=1.0
    )
    config = ExportConfig(output_path=str(tmpdir.join("empty")))

    exporter.export(data, config)

    output_file = str(tmpdir.join("empty.json"))
    assert os.path.exists(output_file)

    with open(output_file, "r") as f:
        payload = json.load(f)

    assert payload["vertices"] == []
    assert payload["indices"] == []
    assert payload["colors"] == []
