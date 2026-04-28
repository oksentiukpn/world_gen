"""
Entry point for the Procedural Planet Generator.
Handles CLI application startup.
"""

from cli.parser import parse_arguments
from core.config import ExportConfig, PlanetConfig
from core.export import export_planet
from core.logger import get_logger
from generation.generator import PlanetGenerator

logger = get_logger(__name__)


def run_cli(args):
    """
    Executes the planet generator in Command Line Interface (CLI) mode.
    Generates the procedural planet based on the provided configuration
    (seed, subdivisions, etc.) and saves the output (e.g., textures, meshes) to disk.

    Args:
        args (argparse.Namespace): The parsed command-line arguments containing
                                   configuration options.
    """
    planet_config = PlanetConfig(
        seed=args.seed,
        subdivisions=args.subdivisions,
    )
    export_config = ExportConfig(
        fmt=args.format,
        output_path=args.output,
        radius=args.radius,
        terrain_scale=args.terrain_scale,
    )

    logger.info("🌍 Starting procedural planet generation CLI...")
    logger.info(
        f"PlanetConfig → Seed: {planet_config.seed} | Subdivisions: {planet_config.subdivisions}"
    )
    logger.info(
        f"ExportConfig → Format: {export_config.fmt} | Output: {export_config.output_path} | "
        f"Radius: {export_config.radius} | TerrainScale: {export_config.terrain_scale}"
    )

    if planet_config.subdivisions >= 8:
        logger.warning(
            f"⚠️  Subdivisions={planet_config.subdivisions} will produce "
            f"~{10 * 4**planet_config.subdivisions + 2:,} vertices. "
            "Expect slow generation and a large output file."
        )

    generator = PlanetGenerator(planet_config)
    planet_data = generator.generate()

    logger.info(f"💾 Saving planet data to {export_config.output_path}...")
    export_planet(planet_data, export_config)
    logger.info("✅ Generation and export fully complete!")


def main():
    """
    The main entry point of the application.
    Parses command-line arguments using the cli.parser module and runs the CLI.
    """
    args = parse_arguments()
    run_cli(args)


if __name__ == "__main__":
    main()
