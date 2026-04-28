"""
Configuration dataclasses for the Procedural Planet Generator.

Centralizes all tuneable parameters in one place so that callers
(CLI, tests, future API) never pass raw primitives across module boundaries.
"""

from dataclasses import dataclass


@dataclass
class PlanetConfig:
    """
    Parameters that describe the planet being generated.

    Attributes:
        seed (int): Master seed for all noise and random operations.
                    Same seed always produces the same planet.
        subdivisions (int): Icosphere subdivision level (1-9).
                    Controls mesh vertex count:
                      1 →      42 vertices  (very low detail)
                      3 →     642 vertices
                      5 →  10 242 vertices  (default, good balance)
                      7 → 163 842 vertices
                      9 → 2 621 442 vertices (very high detail, slow)
        radius (float): Physical radius of the planet in output units (default 1.0).
                    This single value controls two things at once:
                      - Noise frequency at generation time (noise_scale = radius),
                        so larger planets automatically have denser, finer terrain.
                      - Actual sphere size at export time.
                    Effect on terrain feel:
                      radius < 1  → dramatic, coarse terrain (asteroid-like)
                      radius = 1  → default balance
                      radius > 1  → fine, dense detail (large realistic world)
    """

    seed: int = 42
    subdivisions: int = 5
    radius: float = 1.0


@dataclass
class ExportConfig:
    """
    Parameters that control how a generated planet is written to disk.

    Attributes:
        fmt (str): Output format — 'png', 'obj', or 'json'.
        output_path (str): Destination file path (extension auto-appended if missing).
    """

    fmt: str = "png"
    output_path: str = "planet.png"
