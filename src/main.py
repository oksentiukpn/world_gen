"""
Entry point for the Procedural Planet Generator.
Handles execution modes (CLI and Server) and application startup.
"""

import sys


def run_cli(args):
    """
    Executes the planet generator in Command Line Interface (CLI) mode.
    Generates the procedural planet based on the provided configuration
    (seed, resolution, etc.) and saves the output (e.g., textures, meshes) to disk.

    Args:
        args (argparse.Namespace): The parsed command-line arguments containing
                                   configuration options.
    """
    pass


def main():
    """
    The main entry point of the application.
    Parses command-line arguments using the cli.parser module and delegates
    execution to either the CLI runner or the Server runner based on the mode.
    """
    pass


if __name__ == "__main__":
    main()
