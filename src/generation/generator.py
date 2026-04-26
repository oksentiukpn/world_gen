"""
Planet Generator Pipeline.
This module glues together the mathematical core, cellular automata,
and biome generation into a single, cohesive generation pipeline.
"""

from biome.climate import generate_biome_map
from core.fast_types import build_adjacency_list, create_spherical_grid
from core.logger import get_logger
from generation.cellular import simulate_erosion, simulate_tectonics
from generation.noise_3d import generate_heightmap

logger = get_logger(__name__)


class PlanetGenerator:
    """
    Orchestrates the procedural generation of a planet.
    Acts as the main pipeline, calling the mathematical core, cellular automata,
    and biome calculations in the correct order.
    """

    def __init__(self, seed: int = 42, resolution: int = 1024):
        """
        Initializes the PlanetGenerator.

        Args:
            seed (int): The base seed for procedural generation.
            resolution (int): The resolution of the generated planet grid.
        """
        self.seed = seed
        self.resolution = resolution
        # Note: In a stricter Dependency Injection setup, the generation strategies
        # (noise functions, erosion functions) could be passed in here.
        # For now, we use the standard project modules.

    def generate(self) -> dict:
        """
        Executes the full generation pipeline.

        Returns:
            dict: A dictionary containing the generated planet data
                  (e.g., grid, heightmap, biome_map).
        """
        logger.info(
            f"Starting planet generation pipeline (Seed: {self.seed}, Resolution: {self.resolution})"
        )

        try:
            # Step 1: Initialize the spherical grid (Icosphere)
            logger.info("[1/4] Initializing spherical grid (Icosphere)...")
            # Convert abstract resolution to a sane subdivision level (e.g., 4-6)
            subdivisions = (
                max(1, min(7, int(self.resolution // 200)))
                if self.resolution > 10
                else self.resolution
            )
            vertices, faces = create_spherical_grid(subdivisions)

            # Step 2: Generate base heightmap using 3D noise
            logger.info("[2/4] Generating 3D noise heightmap...")
            heightmap = generate_heightmap(vertices, amplitude=5,seed=self.seed)

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

            return {
                "vertices": vertices,
                "faces": faces,
                "heightmap": heightmap,
                "biome_map": biome_map,
            }

        except Exception as e:
            logger.error(
                f"An error occurred during planet generation: {e}", exc_info=True
            )
            raise
