import numpy as np
from src.biome.climate import (
    BLUE,
    BLUE_GREY,
    DARK_GREEN,
    GOLDEN_BROWN,
    LIGHT_GREEN,
    MEDIUM_GREEN,
    PALE_SAND,
    WHITE,
    calculate_moisture,
    calculate_temperature,
    determine_color,
    generate_biome_map,
)


def test_calculate_temperature():
    assert calculate_temperature(0.0, 0.0) == 30.0
    assert calculate_temperature(1.0, 0.0) == -20.0
    assert calculate_temperature(-1.0, 0.0) == -20.0
    assert calculate_temperature(0.0, 1.0) == 10.0


def test_calculate_moisture():
    assert calculate_moisture(0.0) == 450.0
    assert calculate_moisture(1.0) == 0.0
    assert calculate_moisture(0.5) == 225.0


def test_determine_color():
    assert determine_color(10, 100, 0.001) == BLUE
    assert determine_color(-15, 100, 0.5) == WHITE
    assert determine_color(-8, 100, 0.5) == BLUE_GREY
    assert determine_color(10, 200, 0.5) == DARK_GREEN
    assert determine_color(10, 300, 0.5) == MEDIUM_GREEN
    assert determine_color(10, 400, 0.5) == LIGHT_GREEN
    assert determine_color(25, 400, 0.5) == GOLDEN_BROWN
    assert determine_color(25, 450, 0.5) == PALE_SAND


def test_generate_biome_map():
    heightmap = np.array([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
    vertices = np.array(
        [
            [0, 0.0, 0],
            [0, 0.0, 0],
            [0, 0.5, 0],
            [0, 0.5, 0],
            [0, 0.5, 0],
            [0, 1.0, 0],
            [0, 1.0, 0],
            [0, 1.0, 0],
            [0, 1.0, 0],
            [0, 1.0, 0],
        ]
    )
    # water level 0.2 => index 2, sorted_heights[2] = 0.3. So indices 0, 1, 2 are water.
    biome_map = generate_biome_map(heightmap, vertices, water_level=0.2)
    assert biome_map.shape == (10, 3)
    np.testing.assert_array_equal(biome_map[0], BLUE)
    np.testing.assert_array_equal(biome_map[1], BLUE)
    np.testing.assert_array_equal(biome_map[2], BLUE)
    assert not np.array_equal(biome_map[3], BLUE)
