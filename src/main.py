"""
Entry point for the Procedural Planet Generator.
Handles CLI application startup.
"""

import sys

from cli.parser import parse_arguments
from core.logger import get_logger
from generation.generator import PlanetGenerator

logger = get_logger(__name__)


def run_cli(args):
    """
    Executes the planet generator in Command Line Interface (CLI) mode.
    Generates the procedural planet based on the provided configuration
    (seed, resolution, etc.) and saves the output (e.g., textures, meshes) to disk.

    Args:
        args (argparse.Namespace): The parsed command-line arguments containing
                                   configuration options.
    """
    seed = getattr(args, "seed", 42)
    resolution = getattr(args, "resolution", 1024)
    output_path = getattr(args, "output", "planet.png")

    logger.info("🌍 Starting procedural planet generation CLI...")
    logger.info(
        f"Configuration - Seed: {seed} | Resolution: {resolution} | Output: {output_path}"
    )

    generator = PlanetGenerator(seed=seed, resolution=resolution)
    planet_data = generator.generate()

    logger.info(f"✅ Planet generated! Saving output to: {output_path} (Placeholder)")


def main():
    """
    The main entry point of the application.
    Parses command-line arguments using the cli.parser module and runs the CLI.
    """
    args = parse_arguments()
    run_cli(args)


if __name__ == "__main__":
    main()
