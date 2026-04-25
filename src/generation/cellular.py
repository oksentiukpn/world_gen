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

import numpy as np
from numba import njit, prange


# TIP: Uncomment the @njit decorator below when you finish writing the logic
# to make it run 100x faster!
# @njit(parallel=True, fastmath=True)
def simulate_tectonics(heightmap, adjacency_list, iterations, plate_count):
    """
    Simulates tectonic plate movements to create mountain ranges and ocean trenches.

    Args:
        heightmap (numpy.ndarray): 1D array of current elevations for each vertex.
        adjacency_list (numpy.ndarray): 2D array (shape V x 6) containing neighbor indices.
        iterations (int): The number of simulation steps to run.
        plate_count (int): The number of initial tectonic plates to generate.

    Returns:
        numpy.ndarray: The modified heightmap with updated elevations.
    """
    # TODO (Participant 2):
    # 1. Randomly pick `plate_count` vertex indices to be the "seeds" of plates.
    # 2. Grow the plates outward using a breadth-first approach via adjacency_list.
    # 3. Determine movement vectors for each plate.
    # 4. Where plates collide (converge), increase heightmap (mountains).
    # 5. Where plates pull apart (diverge), decrease heightmap (trenches).

    return heightmap


# @njit(parallel=True, fastmath=True)
def simulate_erosion(heightmap, adjacency_list, iterations, erosion_rate):
    """
    Applies hydraulic and thermal erosion to the terrain using cellular automata,
    smoothing sharp cliffs and creating river valleys along the graph edges.

    Args:
        heightmap (numpy.ndarray): 1D array of current elevations.
        adjacency_list (numpy.ndarray): 2D array (shape V x 6) containing neighbor indices.
        iterations (int): The number of erosion cycles to simulate.
        erosion_rate (float): The intensity of the erosion applied per step.

    Returns:
        numpy.ndarray: The eroded heightmap.
    """
    # TODO (Participant 2):
    # 1. Loop `iterations` times.
    # 2. In each iteration, loop through all vertices (prange).
    # 3. For each vertex, find its lowest neighbor in `adjacency_list`.
    # 4. If the height difference is large enough, move some "soil" (height)
    #    from the current vertex to the lower neighbor.

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
