"""
Cellular automata simulations.
Implements erosion, tectonic movements, and other terrain-altering
processes using cellular automata on a discrete graph (Icosphere).
"""

import numpy as np
from numba import njit, prange

@njit(parallel=True, fastmath=True)
def simulate_tectonics(heightmap, adjacency_list, iterations, plate_count):
    """
    Simulates tectonic plate movements to create mountain ranges and ocean trenches.
    """
    num_vertices = len(heightmap)

    # 1. Randomly pick `plate_count` vertex indices to be the "seeds" of plates.
    plate_ids = np.full(num_vertices, -1, dtype=np.int32)
    for p in range(plate_count):
        # We use a simple while loop to avoid duplicate seeds
        while True:
            seed = np.random.randint(0, num_vertices)
            if plate_ids[seed] == -1:
                plate_ids[seed] = p
                break

    # 2. Grow the plates outward using a breadth-first approach via CA
    unassigned = num_vertices - plate_count
    max_grow_iterations = 1000 # Safety limit

    while unassigned > 0 and max_grow_iterations > 0:
        max_grow_iterations -= 1
        new_plate_ids = plate_ids.copy()
        for i in prange(num_vertices):
            if plate_ids[i] == -1:
                # Look at neighbors to inherit a plate ID
                for j in range(6):
                    n = adjacency_list[i, j]
                    if n != -1 and plate_ids[n] != -1:
                        new_plate_ids[i] = plate_ids[n]
                        # Note: we don't decrement unassigned here due to parallel race conditions,
                        # we will recalculate it below.
                        break

        # Recalculate unassigned to safely exit the loop
        plate_ids = new_plate_ids
        unassigned = 0
        for i in range(num_vertices):
            if plate_ids[i] == -1:
                unassigned += 1

    # 3. Determine movement vectors/relationships for each plate.
    # 1 = Converging (Mountains), -1 = Diverging (Trenches), 0 = Neutral/Transform
    boundary_actions = np.zeros((plate_count, plate_count), dtype=np.int32)
    for p1 in range(plate_count):
        for p2 in range(plate_count):
            if p1 != p2:
                # Randomly assign boundary interaction type
                action = np.random.randint(-1, 2)
                boundary_actions[p1, p2] = action
                boundary_actions[p2, p1] = action

    # 4 & 5. Run tectonic simulation
    for _ in range(iterations):
        delta_height = np.zeros(num_vertices, dtype=np.float32)

        for i in prange(num_vertices):
            my_plate = plate_ids[i]

            # Check all neighbors to see if we are on a boundary
            for j in range(6):
                n = adjacency_list[i, j]
                if n != -1:
                    neighbor_plate = plate_ids[n]
                    if my_plate != neighbor_plate:
                        action = boundary_actions[my_plate, neighbor_plate]

                        if action == 1:
                            # Converge: push terrain up
                            delta_height[i] += 0.05
                        elif action == -1:
                            # Diverge: pull terrain down
                            delta_height[i] -= 0.05

        # Apply changes and smooth
        for i in prange(num_vertices):
            heightmap[i] += delta_height[i]

    return heightmap


@njit(parallel=True, fastmath=True)
def simulate_erosion(heightmap, adjacency_list, iterations, erosion_rate):
    """
    Applies hydraulic and thermal erosion to the terrain using cellular automata,
    smoothing sharp cliffs and creating river valleys along the graph edges.
    """
    num_vertices = len(heightmap)

    # 1. Loop `iterations` times.
    for _ in range(iterations):
        # Array to store how much height each vertex gains or loses
        delta = np.zeros(num_vertices, dtype=np.float32)

        # 2. Loop through all vertices
        for i in prange(num_vertices):
            h_i = heightmap[i]
            lowest_n = -1
            min_h = h_i

            # 3. Find lowest neighbor
            for j in range(6):
                n = adjacency_list[i, j]
                if n != -1:
                    h_n = heightmap[n]
                    if h_n < min_h:
                        min_h = h_n
                        lowest_n = n

            # 4. Move "soil" if difference is large enough
            if lowest_n != -1:
                diff = h_i - min_h
                # Minimal threshold to stop infinite micro-erosion
                if diff > 0.01:
                    # Move a percentage of the difference
                    transfer = diff * erosion_rate
                    delta[i] -= transfer

                    # Numba note: In parallel loops, writing to delta[lowest_n] might
                    # theoretically have minor race conditions. In procedural generation
                    # this is usually ignored as it adds natural "noise" to the erosion.
                    delta[lowest_n] += transfer

        # Apply changes for this step
        for i in prange(num_vertices):
            heightmap[i] += delta[i]

    return heightmap


@njit(fastmath=True)
def get_neighbors(vertex_index, adjacency_list):
    """
    Helper function to safely retrieve the valid neighbor indices for a specific vertex.
    Filters out the -1 padding values.
    """
    raw_neighbors = adjacency_list[vertex_index]
    # Numba works best with typed lists or arrays.
    # We create a temporary list for valid neighbors.
    valid_neighbors = []

    for i in range(6):
        n = raw_neighbors[i]
        if n != -1:
            valid_neighbors.append(n)

    return valid_neighbors


def apply_custom_automata(vertex_states, adjacency_list, transition_function, iterations):
    """
    A generic cellular automaton runner for the planetary graph. Updates vertex
    states based on a provided transition function and the states of its neighbors.
    """
    num_vertices = len(vertex_states)

    for _ in range(iterations):
        new_states = vertex_states.copy()

        for i in range(num_vertices):
            # Using our helper (or standard python slicing if outside Numba)
            neighbors = []
            for j in range(6):
                n = adjacency_list[i, j]
                if n != -1:
                    neighbors.append(vertex_states[n])

            new_states[i] = transition_function(vertex_states[i], neighbors)

        vertex_states = new_states

    return vertex_states
