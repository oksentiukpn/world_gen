import numpy as np
from src.core.export.base import FALLBACK_COLOR, ensure_extension, get_color


def test_get_color_with_valid_biome_map():
    biome_map = np.array([[255, 0, 0], [0, 255, 0]], dtype=np.uint8)
    assert get_color(biome_map, 0) == (255, 0, 0)
    assert get_color(biome_map, 1) == (0, 255, 0)


def test_get_color_with_missing_or_invalid_biome_map():
    assert get_color(None, 0) == FALLBACK_COLOR
    assert get_color(np.array([1, 2, 3]), 0) == FALLBACK_COLOR
    assert get_color(np.array([[1, 2], [3, 4]]), 0) == FALLBACK_COLOR


def test_ensure_extension():
    assert ensure_extension("test.txt", ".txt") == "test.txt"
    assert ensure_extension("test", ".txt") == "test.txt"
    assert ensure_extension("test.obj", ".txt") == "test.obj.txt"
