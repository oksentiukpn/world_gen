"""
Planet Generator Pipeline.
This module glues together the mathematical core, cellular automata,
and biome generation into a single, cohesive generation pipeline.
"""

import numpy as np
from biome.climate import generate_biome_map
from core.config import PlanetConfig
from core.fast_types import build_adjacency_list, create_spherical_grid
from core.logger import get_logger
from core.planet_data import PlanetData
from generation.cellular import simulate_tectonics
from generation.noise_3d import generate_heightmap
from numba import njit

logger = get_logger(__name__)


@njit
def normalize(data):
    low = np.min(data)
    high = np.max(data)
    span = high - low
    if span != 0:
        return (data - low) / span
    return data - low


class PlanetGenerator:
    """
    Orchestrates the procedural generation of a planet.
    Acts as the main pipeline, calling the mathematical core, cellular automata,
    and biome calculations in the correct order.
    """

    def __init__(self, config: PlanetConfig | None = None, **kwargs):
        """
        Initializes the PlanetGenerator.

        Args:
            config (PlanetConfig): Generation parameters. If omitted, a default
                                   PlanetConfig() is used. Keyword arguments
                                   (seed, subdivisions) are forwarded to PlanetConfig
                                   for convenience: PlanetGenerator(seed=42, subdivisions=5).
        """
        if config is None:
            config = PlanetConfig(**kwargs)
        self.config = config

    def generate(self) -> PlanetData:
        """
        Executes the full generation pipeline.

        Returns:
            PlanetData: Typed container with vertices, faces, heightmap, and biome_map.
        """
        logger.info(
            f"Starting planet generation pipeline "
            f"(Seed: {self.config.seed}, Subdivisions: {self.config.subdivisions})"
        )

        try:
            # Step 1: Initialize the spherical grid (Icosphere)
            logger.info("[1/4] Initializing spherical grid (Icosphere)...")
            vertices, faces = create_spherical_grid(self.config.subdivisions)

            # Step 2: Apply cellular automata (Tectonics)
            logger.info("[2/4] Simulating tectonics...")
            n_points = vertices.shape[0]
            base_heightmap = np.ones(n_points, dtype=np.float32)
            adjacency_list = build_adjacency_list(n_points, faces)

            heightmap = simulate_tectonics(
                base_heightmap,
                adjacency_list,
                iterations=self.config.plate_iterations,
                plate_count=self.config.plate_count,
                radius=self.config.range_radius,
                seed=self.config.seed,
            )

            heightmap = normalize(heightmap) * self.config.range_amplitude

            # Step 3: Generate base heightmap using 3D noise
            logger.info("[3/4] Generating 3D noise heightmap...")
            noise_heightmap = generate_heightmap(
                vertices,
                seed=self.config.seed,
                noise_scale=self.config.noise_scale,
                octaves=self.config.octaves,
                persistence=self.config.persistence,
                lacunarity=self.config.lacunarity,
                amplitude=self.config.amplitude,
                # water_level=self.config.water_level,
                sharpness_strength=self.config.sharpness_strength,
            )

            heightmap = heightmap * noise_heightmap + noise_heightmap
            heightmap = np.maximum(
                heightmap, self.config.water_level * np.max(heightmap)
            )

            # Step 4: Calculate climate and biomes
            logger.info("[4/4] Calculating climate matrices and biomes...")
            biome_map = generate_biome_map(
                heightmap, vertices, water_level=self.config.water_level
            )

            logger.info("✅ Planet generation pipeline completed successfully.")

            return PlanetData(
                vertices=vertices,
                faces=faces,
                heightmap=heightmap,
                biome_map=biome_map,
                radius=self.config.radius,
            )

        except Exception as e:
            logger.error(
                f"An error occurred during planet generation: {e}", exc_info=True
            )
            raise
