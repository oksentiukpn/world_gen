"""
Cellular automata simulations.
Implements erosion, tectonic movements, and other terrain-altering
processes using cellular automata on a discrete graph (Icosphere).

INSTRUCTIONS FOR PARTICIPANT 2 (LOGIC / CELLULAR AUTOMATA):
-----------------------------------------------------------
1. The planet is no longer a 2D grid! It is a 3D graph (Icosphere).
2. Instead of checking grid[x][y], you will loop through a 1D array of vertices.
3. To find the neighbors of vertex `i`, look at `adjacency_list[i]`.
   This returns an array of exactly 6 integers.
   IMPORTANT: If a neighbor is -1, it means it's empty (base vertices only have 5 neighbors). Ignore -1!
4. Use Numba! Wrap your heavy loops in @njit(parallel=True, fastmath=True)
   and use `prange` instead of `range` to make the simulation run in real-time.
"""

import math

import numpy as np
from numba import njit, prange


@njit(parallel=True, fastmath=True)
def simulate_tectonics(heightmap, adjacency_list, iterations, plate_count, radius=1.0):
    """
    Simulates tectonic plate movements to create mountain ranges and ocean trenches.

    Args:
        heightmap (numpy.ndarray): 1D array of current elevations for each vertex.
        adjacency_list (numpy.ndarray): 2D array (shape V x 6) containing neighbor indices.
        iterations (int): The number of simulation steps to run.
        plate_count (int): The number of initial tectonic plates to generate.
        radius (float): The radius of the planet.

    Returns:
        numpy.ndarray: The modified heightmap with updated elevations.
    """
    num_vertices = len(heightmap)
    plate_ids = np.zeros(num_vertices, dtype=np.int32)

    for i in range(1, plate_count + 1):
        seed_idx = np.random.randint(0, num_vertices)
        plate_ids[seed_idx] = i

    # Grow the plates outward using a cellular automata approach with randomness for organic shapes
    # Pre-assign a "growth resistance" to each vertex to make the expansion highly irregular.
    # This forces plates to flow *around* highly resistant nodes, creating deeply jagged, crooked faults.
    resistance = np.random.rand(num_vertices) * 0.90

    unassigned_count = num_vertices - plate_count
    while unassigned_count > 0:
        new_plate_ids = plate_ids.copy()
        for i in prange(num_vertices):
            if plate_ids[i] == 0:
                # Only attempt to claim if we overcome resistance
                if np.random.rand() > resistance[i]:
                    valid_count = 0
                    valid_plates = np.zeros(6, dtype=np.int32)

                    for j in range(6):
                        neighbor = adjacency_list[i, j]
                        if neighbor != -1 and plate_ids[neighbor] != 0:
                            valid_plates[valid_count] = plate_ids[neighbor]
                            valid_count += 1

                    if valid_count > 0:
                        # Pick a random valid neighbor to inherit from
                        chosen_idx = np.random.randint(0, valid_count)
                        new_plate_ids[i] = valid_plates[chosen_idx]

        unassigned_count = 0
        for i in range(num_vertices):
            if new_plate_ids[i] == 0:
                unassigned_count += 1

        plate_ids = new_plate_ids

    # Identify plate boundaries
    dist_conv = np.full(num_vertices, 999.0, dtype=np.float32)
    dist_div = np.full(num_vertices, 999.0, dtype=np.float32)

    # Generate CA-based active zones to chunk the fault lines into isolated mountain ranges.
    # This prevents the mountains from tracing the entire plate outline.
    active_zones = np.zeros(num_vertices, dtype=np.bool_)
    num_zones = max(10, int(25 * radius))
    for _ in range(num_zones):
        active_zones[np.random.randint(0, num_vertices)] = True

    zone_expansion = max(5, int(10 * radius))
    for _ in range(zone_expansion):
        new_active = active_zones.copy()
        for i in prange(num_vertices):
            if active_zones[i]:
                for j in range(6):
                    n = adjacency_list[i, j]
                    if n != -1:
                        new_active[n] = True
        active_zones = new_active

    for i in prange(num_vertices):
        my_plate = plate_ids[i]
        for j in range(6):
            neighbor = adjacency_list[i, j]
            if neighbor != -1:
                neighbor_plate = plate_ids[neighbor]
                if my_plate != neighbor_plate:
                    # Only form mountains if the fault line passes through an active zone
                    if active_zones[i]:
                        min_p = min(my_plate, neighbor_plate)
                        max_p = max(my_plate, neighbor_plate)
                        interaction = (min_p * 7 + max_p * 13) % 3

                        if interaction == 1:
                            dist_conv[i] = 0.0
                        elif interaction == 0:
                            dist_div[i] = 0.0

    # Cellular Automata Distance Transform (flood fill distances)
    # Scale max_dist by radius so mountains stay proportionally wide but not overly massive
    max_dist = max(2.0, radius * 3.0)
    for _ in range(int(max_dist)):
        new_dist_conv = dist_conv.copy()
        new_dist_div = dist_div.copy()
        for i in prange(num_vertices):
            for j in range(6):
                neighbor = adjacency_list[i, j]
                if neighbor != -1:
                    if dist_conv[neighbor] + 1 < new_dist_conv[i]:
                        new_dist_conv[i] = dist_conv[neighbor] + 1
                    if dist_div[neighbor] + 1 < new_dist_div[i]:
                        new_dist_div[i] = dist_div[neighbor] + 1
        dist_conv = new_dist_conv
        dist_div = new_dist_div

    # Apply vast, sweeping height changes based on distance
    for i in prange(num_vertices):
        # Convergent: Wide, majestic mountains
        if dist_conv[i] < max_dist:
            normalized_dist = dist_conv[i] / max_dist
            # Cosine falloff for smooth, natural bell curve (1.0 at center, 0.0 at edge)
            falloff = 0.5 * (1.0 + math.cos(normalized_dist * math.pi))
            # Random variation for rugged foothills
            noise = 1.0 + (np.random.rand() * 0.6 - 0.3)
            # Uplift
            heightmap[i] += 4.0 * falloff * noise

        # Divergent: Deep, wide oceanic trenches
        if dist_div[i] < max_dist / 2:
            normalized_dist = dist_div[i] / (max_dist / 2.0)
            falloff = 0.5 * (1.0 + math.cos(normalized_dist * math.pi))
            heightmap[i] -= 1.5 * falloff

    # Final overall thermal erosion to seamlessly blend the huge ranges into the noise
    for _ in range(3):
        smoothed_heightmap = heightmap.copy()
        for i in prange(num_vertices):
            total_h = heightmap[i]
            count = 1
            for j in range(6):
                neighbor = adjacency_list[i, j]
                if neighbor != -1:
                    total_h += heightmap[neighbor]
                    count += 1
            # 70% original, 30% neighbors for a buttery smooth blend
            smoothed_heightmap[i] = heightmap[i] * 0.7 + (total_h / count) * 0.3
        heightmap = smoothed_heightmap

    return heightmap


@njit(fastmath=True)
def get_neighbors(vertex_index, adjacency_list):
    """
    Helper function to safely retrieve the valid neighbor indices for a specific vertex.
    Filters out the -1 padding values.

    Args:
        vertex_index (int): The index of the target vertex.
        adjacency_list (numpy.ndarray): The full graph adjacency list.

    Returns:
        list: Valid neighbor indices.
    """
    raw_neighbors = adjacency_list[vertex_index]
    valid_neighbors = []

    for i in range(6):
        n = raw_neighbors[i]
        if n != -1:
            valid_neighbors.append(n)

    return valid_neighbors


def apply_custom_automata(
    vertex_states, adjacency_list, transition_function, iterations
):
    """
    A generic cellular automaton runner for the planetary graph. Updates vertex
    states based on a provided transition function and the states of its neighbors.

    Args:
        vertex_states (numpy.ndarray): The initial state of each vertex.
        adjacency_list (numpy.ndarray): The graph structure connecting vertices.
        transition_function (callable): A function that computes the next state.
        iterations (int): The number of generations to simulate.

    Returns:
        numpy.ndarray: The final states after all iterations.
    """
    # TODO (Participant 2): Optional wrapper if you want to abstract the CA loop.
    return vertex_states
