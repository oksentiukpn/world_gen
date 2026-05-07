import numpy as np
from src.core.fast_types import (
    build_adjacency_list,
    create_faces_array,
    create_spherical_grid,
    create_vector3_array,
    fast_distance_3d,
    normalize_vectors_fast,
)


def test_create_vector3_array():
    arr = create_vector3_array(10)
    assert arr.shape == (10, 3)
    assert arr.dtype == np.float32


def test_normalize_vectors_fast():
    vectors = np.array(
        [[1.0, 0.0, 0.0], [0.0, 2.0, 0.0], [1.0, 1.0, 1.0], [0.0, 0.0, 0.0]],
        dtype=np.float32,
    )
    norm = normalize_vectors_fast(vectors)

    np.testing.assert_allclose(norm[0], [1.0, 0.0, 0.0])
    np.testing.assert_allclose(norm[1], [0.0, 1.0, 0.0])

    # sqrt(3) = 1.732...
    expected_c = 1.0 / np.sqrt(3)
    np.testing.assert_allclose(norm[2], [expected_c, expected_c, expected_c], rtol=1e-5)
    np.testing.assert_allclose(norm[3], [0.0, 0.0, 0.0])


def test_create_faces_array():
    arr = create_faces_array(5)
    assert arr.shape == (5, 3)
    assert arr.dtype == np.int32


def test_create_spherical_grid():
    # Test level 0
    v, f = create_spherical_grid(0)
    assert v.shape[0] == 12
    assert f.shape[0] == 20
    assert v.shape[1] == 3
    assert f.shape[1] == 3

    # Test level 1
    v, f = create_spherical_grid(1)
    assert v.shape[0] == 42
    assert f.shape[0] == 80


def test_fast_distance_3d():
    p1 = np.array([0.0, 0.0, 0.0])
    p2 = np.array([3.0, 4.0, 0.0])
    assert np.isclose(fast_distance_3d(p1, p2), 5.0)


def test_build_adjacency_list():
    faces = np.array([[0, 1, 2], [0, 2, 3], [0, 3, 1]], dtype=np.int32)

    adj = build_adjacency_list(4, faces)

    assert adj.shape == (4, 6)
    assert set(adj[0]) - {-1} == {1, 2, 3}
    assert set(adj[1]) - {-1} == {0, 2, 3}
    assert set(adj[2]) - {-1} == {0, 1, 3}
    assert set(adj[3]) - {-1} == {0, 1, 2}
