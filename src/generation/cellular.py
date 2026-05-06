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


@njit(fastmath=True)
def _hash_uint32(index, seed, salt):
    """Returns a deterministic 32-bit hash for the given inputs."""
    mask = 0xFFFFFFFF

    state = (
        index * 1664525
        + seed * 1013904223
        + salt * 374761393
        + 0x9E3779B9
    ) & mask

    word = ((state >> ((state >> 28) + 4)) ^ state) * 277803737
    word &= mask

    return (word >> 22) ^ word


@njit(fastmath=True)
def _hash01(index, seed, salt):
    """Maps a deterministic hash to the range [0, 1)."""
    return _hash_uint32(index, seed, salt) * (1.0 / 4294967296.0)


@njit(fastmath=True)
def _select_seed_vertices(num_vertices, count, seed, salt):
    """
    Deterministically selects unique vertex indices with the smallest hash values.
    This produces stable, pseudo-random seed placement for the same master seed.
    """
    actual_count = min(count, num_vertices)
    selected_indices = np.full(actual_count, -1, dtype=np.int32)
    selected_hashes = np.full(actual_count, 0xFFFFFFFF, dtype=np.int64)

    if actual_count == 0:
        return selected_indices

    filled = 0
    for vertex in range(num_vertices):
        vertex_hash = _hash_uint32(vertex, seed, salt)

        if filled < actual_count:
            selected_indices[filled] = vertex
            selected_hashes[filled] = vertex_hash
            filled += 1
            continue

        max_pos = 0
        max_hash = selected_hashes[0]
        max_idx = selected_indices[0]

        for j in range(1, actual_count):
            hash_j = selected_hashes[j]
            idx_j = selected_indices[j]
            if hash_j > max_hash or (hash_j == max_hash and idx_j > max_idx):
                max_pos = j
                max_hash = hash_j
                max_idx = idx_j

        if vertex_hash < max_hash or (vertex_hash == max_hash and vertex < max_idx):
            selected_indices[max_pos] = vertex
            selected_hashes[max_pos] = vertex_hash

    for i in range(actual_count):
        min_pos = i
        min_hash = selected_hashes[i]
        min_idx = selected_indices[i]

        for j in range(i + 1, actual_count):
            hash_j = selected_hashes[j]
            idx_j = selected_indices[j]
            if hash_j < min_hash or (hash_j == min_hash and idx_j < min_idx):
                min_pos = j
                min_hash = hash_j
                min_idx = idx_j

        if min_pos != i:
            tmp_idx = selected_indices[i]
            tmp_hash = selected_hashes[i]
            selected_indices[i] = selected_indices[min_pos]
            selected_hashes[i] = selected_hashes[min_pos]
            selected_indices[min_pos] = tmp_idx
            selected_hashes[min_pos] = tmp_hash

    return selected_indices


@njit(parallel=True, fastmath=True)
def simulate_tectonics(
    heightmap, adjacency_list, iterations, plate_count, radius=1.0, seed=0
):
    """
    Simulates tectonic plate movements to create mountain ranges and ocean trenches.

    Args:
        heightmap (numpy.ndarray): 1D array of current elevations for each vertex.
        adjacency_list (numpy.ndarray): 2D array (shape V x 6) containing neighbor indices.
        iterations (int): The number of simulation steps to run.
        plate_count (int): The number of initial tectonic plates to generate.
        radius (float): The radius of the planet.
        seed (int): Master seed for deterministic tectonic generation.

    Returns:
        numpy.ndarray: The modified heightmap with updated elevations.
    """
    num_vertices = len(heightmap)

    if num_vertices == 0 or plate_count <= 0:
        return heightmap

    plate_ids = np.zeros(num_vertices, dtype=np.int32)
    seed_vertices = _select_seed_vertices(num_vertices, plate_count, seed, 11)
    actual_plate_count = len(seed_vertices)

    for i in range(actual_plate_count):
        plate_ids[seed_vertices[i]] = i + 1

    # Grow the plates outward using a cellular automata approach with deterministic
    # resistance per vertex so the same seed always produces the same fault contours.
    resistance = np.empty(num_vertices, dtype=np.float32)
    for i in prange(num_vertices):
        resistance[i] = _hash01(i, seed, 101) * 0.90

    unassigned_count = num_vertices - actual_plate_count
    growth_step = 0
    while unassigned_count > 0:
        new_plate_ids = plate_ids.copy()
        growth_step += 1
        growth_offset = growth_step * num_vertices

        for i in prange(num_vertices):
            if plate_ids[i] == 0:
                claim_roll = _hash01(i + growth_offset, seed, 131)
                if claim_roll > resistance[i]:
                    valid_count = 0
                    valid_plates = np.zeros(6, dtype=np.int32)

                    for j in range(6):
                        neighbor = adjacency_list[i, j]
                        if neighbor != -1 and plate_ids[neighbor] != 0:
                            valid_plates[valid_count] = plate_ids[neighbor]
                            valid_count += 1

                    if valid_count > 0:
                        chosen_idx = _hash_uint32(i + growth_offset, seed, 151) % valid_count
                        new_plate_ids[i] = valid_plates[chosen_idx]

        progress_made = False
        unassigned_count = 0
        for i in range(num_vertices):
            if plate_ids[i] == 0 and new_plate_ids[i] != 0:
                progress_made = True
            if new_plate_ids[i] == 0:
                unassigned_count += 1

        if not progress_made and unassigned_count > 0:
            force_offset = growth_offset + num_vertices
            for i in range(num_vertices):
                if new_plate_ids[i] == 0:
                    valid_count = 0
                    valid_plates = np.zeros(6, dtype=np.int32)

                    for j in range(6):
                        neighbor = adjacency_list[i, j]
                        if neighbor != -1 and plate_ids[neighbor] != 0:
                            valid_plates[valid_count] = plate_ids[neighbor]
                            valid_count += 1

                    if valid_count > 0:
                        chosen_idx = _hash_uint32(i + force_offset, seed, 171) % valid_count
                        new_plate_ids[i] = valid_plates[chosen_idx]

            unassigned_count = 0
            for i in range(num_vertices):
                if new_plate_ids[i] == 0:
                    unassigned_count += 1

        plate_ids = new_plate_ids

    # Identify plate boundaries
    dist_conv = np.full(num_vertices, 999.0, dtype=np.float32)
    dist_div = np.full(num_vertices, 999.0, dtype=np.float32)
    conv_strength = np.zeros(num_vertices, dtype=np.float32)
    div_strength = np.zeros(num_vertices, dtype=np.float32)

    # Generate deterministic active zones to chunk fault lines into isolated
    # mountain ranges while preserving reproducibility.
    active_zones = np.zeros(num_vertices, dtype=np.bool_)
    num_zones = max(10, int(25 * radius))
    zone_vertices = _select_seed_vertices(num_vertices, num_zones, seed, 211)
    for i in range(len(zone_vertices)):
        active_zones[zone_vertices[i]] = True

    zone_expansion = max(5, int(10 * radius))
    for _ in range(zone_expansion):
        new_active = np.empty_like(active_zones)
        for i in prange(num_vertices):
            is_active = active_zones[i]
            if not is_active:
                for j in range(6):
                    n = adjacency_list[i, j]
                    if n != -1 and active_zones[n]:
                        is_active = True
                        break
            new_active[i] = is_active
        active_zones = new_active

    for i in prange(num_vertices):
        my_plate = plate_ids[i]
        local_conv_strength = 0.0
        local_div_strength = 0.0
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
                        pair_key = min_p * 4099 + max_p * 8191
                        pair_scale = 0.85 + 0.30 * _hash01(pair_key, seed, 251)

                        if interaction == 1:
                            dist_conv[i] = 0.0
                            if pair_scale > local_conv_strength:
                                local_conv_strength = pair_scale
                        elif interaction == 0:
                            dist_div[i] = 0.0
                            if pair_scale > local_div_strength:
                                local_div_strength = pair_scale

        if dist_conv[i] == 0.0:
            conv_strength[i] = 4.0 * local_conv_strength
        if dist_div[i] == 0.0:
            div_strength[i] = 1.5 * local_div_strength

    # Cellular Automata Distance Transform (flood fill distances)
    # Scale max_dist by radius so mountains stay proportionally wide but not overly massive
    max_dist = max(2.0, radius * 3.0)
    for _ in range(int(max_dist)):
        new_dist_conv = dist_conv.copy()
        new_dist_div = dist_div.copy()
        new_conv_strength = conv_strength.copy()
        new_div_strength = div_strength.copy()
        for i in prange(num_vertices):
            best_conv_dist = new_dist_conv[i]
            best_div_dist = new_dist_div[i]
            best_conv_strength = new_conv_strength[i]
            best_div_strength = new_div_strength[i]

            for j in range(6):
                neighbor = adjacency_list[i, j]
                if neighbor != -1:
                    conv_candidate = dist_conv[neighbor] + 1.0
                    neighbor_conv_strength = conv_strength[neighbor]
                    if conv_candidate < best_conv_dist or (
                        conv_candidate == best_conv_dist
                        and neighbor_conv_strength > best_conv_strength
                    ):
                        best_conv_dist = conv_candidate
                        best_conv_strength = neighbor_conv_strength

                    div_candidate = dist_div[neighbor] + 1.0
                    neighbor_div_strength = div_strength[neighbor]
                    if div_candidate < best_div_dist or (
                        div_candidate == best_div_dist
                        and neighbor_div_strength > best_div_strength
                    ):
                        best_div_dist = div_candidate
                        best_div_strength = neighbor_div_strength

            new_dist_conv[i] = best_conv_dist
            new_conv_strength[i] = best_conv_strength
            new_dist_div[i] = best_div_dist
            new_div_strength[i] = best_div_strength
        dist_conv = new_dist_conv
        dist_div = new_dist_div
        conv_strength = new_conv_strength
        div_strength = new_div_strength

    # Apply vast, sweeping height changes based on distance with only smooth,
    # deterministic coefficients for stable, natural-looking ridges.
    for i in prange(num_vertices):
        # Convergent: Wide, majestic mountains
        if dist_conv[i] < max_dist:
            normalized_dist = dist_conv[i] / max_dist
            falloff = 0.5 * (1.0 + math.cos(normalized_dist * math.pi))
            heightmap[i] += conv_strength[i] * falloff

        # Divergent: Deep, wide oceanic trenches
        if dist_div[i] < max_dist / 2:
            normalized_dist = dist_div[i] / (max_dist / 2.0)
            falloff = 0.5 * (1.0 + math.cos(normalized_dist * math.pi))
            heightmap[i] -= div_strength[i] * falloff

    # Final overall thermal erosion to seamlessly blend the huge ranges into the noise
    for _ in range(max(1, iterations * 2)):
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
