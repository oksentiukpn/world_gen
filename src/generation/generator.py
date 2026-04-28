"""
Planet Generator Pipeline.
This module glues together the mathematical core, cellular automata,
and biome generation into a single, cohesive generation pipeline.
"""

from biome.climate import generate_biome_map
from core.config import PlanetConfig
from core.fast_types import build_adjacency_list, create_spherical_grid
from core.logger import get_logger
from core.planet_data import PlanetData
from generation.cellular import simulate_erosion, simulate_tectonics
from generation.noise_3d import generate_heightmap

logger = get_logger(__name__)


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

            # Step 2: Generate base heightmap using 3D noise
            logger.info("[2/4] Generating 3D noise heightmap...")
            # noise_scale = radius: larger planet → higher noise frequency
            # → denser, finer terrain features automatically
            heightmap = generate_heightmap(
                vertices,
                amplitude=5,
                seed=self.config.seed,
                noise_scale=self.config.radius,
            )

            # Step 3: Apply cellular automata (Tectonics and Erosion)
            logger.info("[3/4] Simulating tectonics and erosion...")
            adjacency_list = build_adjacency_list(vertices.shape[0], faces)
            heightmap = simulate_tectonics(
                heightmap, adjacency_list, iterations=10, plate_count=15
            )
            heightmap = simulate_erosion(
                heightmap, adjacency_list, iterations=5, erosion_rate=0.01
            )

            # Step 4: Calculate climate and biomes
            logger.info("[4/4] Calculating climate matrices and biomes...")
            biome_map = generate_biome_map(heightmap, vertices)

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
