"""
Configuration dataclasses for the Procedural Planet Generator.

Centralizes all tuneable parameters in one place so that callers
(CLI, tests, future API) never pass raw primitives across module boundaries.
"""

from dataclasses import dataclass


@dataclass
class PlanetConfig:
    """
    Parameters that control procedural planet generation.

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
    """

    seed: int = 42
    subdivisions: int = 5


@dataclass
class ExportConfig:
    """
    Parameters that control how a generated planet is serialized to disk.

    Attributes:
        fmt (str): Output format — 'png', 'obj', or 'json'.
        output_path (str): Destination file path (extension auto-appended if missing).
        radius (float): Base radius of the planet sphere in output units (default 1.0).
                        Scales the planet size without affecting terrain height.
        terrain_scale (float): How much one unit of heightmap displaces a vertex
                               in output units (default 0.02).
                               Independent from radius — changing radius does NOT
                               change mountain height unless you change this too.
    """

    fmt: str = "png"
    output_path: str = "planet.png"
    radius: float = 1.0
    terrain_scale: float = 0.02
