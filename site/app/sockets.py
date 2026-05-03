import logging
import os
import sys

import numpy as np
from flask_socketio import SocketIO, emit

# Ensure src is in python path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "src"))
)

from biome.climate import generate_biome_map
from core.config import PlanetConfig
from core.fast_types import build_adjacency_list, create_spherical_grid
from generation.cellular import simulate_erosion, simulate_tectonics
from generation.noise_3d import generate_heightmap

socketio = SocketIO(cors_allowed_origins="*")
logger = logging.getLogger(__name__)


@socketio.on("generate_planet")
def handle_generate_planet(data):
    logger.info(f"Received generate_planet request: {data}")

    seed = int(data.get("seed", 42))
    radius = float(data.get("radius", 10.0))
    subdivisions = int(data.get("subdivisions", 4))
    noise_scale = float(data.get("noise_scale", 1))
    octaves = int(data.get("octaves", 4))
    persistence = float(data.get("persistence", 0.4))
    lacunarity = float(data.get("lacunarity", 2))
    amplitude = float(data.get("amplitude", 1))
    water_level = float(data.get("water_level", 0.375))
    sharpness_strength = float(data.get("sharpness_strength", 1))

    # Cap subdivisions to avoid crashing the server/browser during real-time preview
    if subdivisions > 8:
        subdivisions = 8

    config = PlanetConfig(
        seed=seed,
        radius=radius,
        subdivisions=subdivisions,
        noise_scale=noise_scale,
        octaves=octaves,
        persistence=persistence,
        lacunarity=lacunarity,
        amplitude=amplitude,
        water_level=water_level,
        sharpness_strength=sharpness_strength
    )

    try:
        # Step 1: Base Mesh
        emit("step_progress", {"step": 1, "message": "Initializing spherical grid..."})
        socketio.sleep(0)  # Yield control

        vertices, faces = create_spherical_grid(config.subdivisions)

        # Force types before tobytes() to ensure JS reads them correctly
        # Numba/Numpy can sometimes implicitly upcast to float64 or int64
        v_bytes = vertices.astype(np.float32).tobytes()
        f_bytes = faces.astype(np.uint32).tobytes()

        emit(
            "step_base",
            {"vertices": v_bytes, "faces": f_bytes, "radius": config.radius},
        )
        socketio.sleep(0.1)  # Small delay for UI animation if needed

        # Step 2: Noise (Base)
        emit(
            "step_progress", {"step": 2, "message": "Generating 3D noise heightmap..."}
        )
        socketio.sleep(0)

        heightmap = generate_heightmap(
            vertices,
            seed=config.seed,
            noise_scale=config.noise_scale,
            octaves=config.octaves,
            persistence=config.persistence,
            lacunarity=config.lacunarity,
            amplitude=config.amplitude,
            water_level=config.water_level,
            sharpness_strength=config.sharpness_strength
        )

        h_bytes = heightmap.astype(np.float32).tobytes()
        emit("step_noise", {"heightmap": h_bytes})
        socketio.sleep(0.1)

        # Step 3: Erosion and Tectonics
        emit(
            "step_progress",
            {"step": 3, "message": "Simulating tectonics and erosion..."},
        )
        socketio.sleep(0)

        adjacency_list = build_adjacency_list(vertices.shape[0], faces)
        heightmap = simulate_tectonics(
            heightmap, adjacency_list, iterations=10, plate_count=15
        )
        heightmap = simulate_erosion(
            heightmap, adjacency_list, iterations=5, erosion_rate=0.01
        )

        h_refined_bytes = heightmap.astype(np.float32).tobytes()
        emit("step_noise_refined", {"heightmap": h_refined_bytes})
        socketio.sleep(0.1)

        # Step 4: Biomes
        emit(
            "step_progress", {"step": 4, "message": "Calculating climate and biomes..."}
        )
        socketio.sleep(0)

        # biome_map = generate_biome_map(heightmap, vertices)

        # b_bytes = biome_map.astype(np.uint8).tobytes()
        # emit("step_biome", {"biome_map": b_bytes})
        # socketio.sleep(0.1)

        emit("generation_complete", {"message": "Planet generated successfully!"})

    except Exception as e:
        logger.error(f"Error during generation: {e}", exc_info=True)
        emit("generation_error", {"message": str(e)})
