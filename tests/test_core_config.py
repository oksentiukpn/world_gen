from src.core.config import ExportConfig, PlanetConfig


def test_planet_config_defaults():
    config = PlanetConfig()
    assert config.seed == 67
    assert config.subdivisions == 5
    assert config.radius == 2.0
    assert config.noise_scale == 1.0
    assert config.octaves == 5
    assert config.persistence == 0.4
    assert config.lacunarity == 2.0
    assert config.amplitude == 20
    assert config.water_level == 0.275
    assert config.sharpness_strength == 5
    assert config.plate_iterations == 5
    assert config.plate_count == 15
    assert config.range_radius == 2
    assert config.range_amplitude == 1


def test_planet_config_custom():
    config = PlanetConfig(seed=42, subdivisions=3, radius=1.0)
    assert config.seed == 42
    assert config.subdivisions == 3
    assert config.radius == 1.0


def test_export_config_defaults():
    config = ExportConfig()
    assert config.fmt == "png"
    assert config.output_path == "planet.png"


def test_export_config_custom():
    config = ExportConfig(fmt="obj", output_path="test.obj")
    assert config.fmt == "obj"
    assert config.output_path == "test.obj"
