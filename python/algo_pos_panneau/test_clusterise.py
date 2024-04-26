from clusterise import clusterise_mat, extract_clusters
import numpy as np

def test_clusterise():
    compat_mat = np.array([
        [1,1,1,0,0,0],
        [1,1,1,1,0,0],
        [1,1,1,1,0,1],
        [0,0,1,1,1,1],
        [0,0,0,1,1,1],
        [0,0,0,1,1,1]
        ], dtype=np.uint8)
    
    compat_mat = clusterise_mat(compat_mat)

    compat_mat_cluster = np.array([
        [1,1,1,0,0,0],
        [1,1,1,0,0,0],
        [1,1,1,0,0,0],
        [0,0,0,1,1,1],
        [0,0,0,1,1,1],
        [0,0,0,1,1,1]
        ], dtype=np.uint8)
    
    np.testing.assert_array_equal(compat_mat, compat_mat_cluster)

def test_extract_clusters():
    compat_mat_cluster = np.array([
        [1,1,1,0,0,0],
        [1,1,1,0,0,0],
        [1,1,1,0,0,0],
        [0,0,0,1,0,0],
        [0,0,0,0,1,1],
        [0,0,0,0,1,1]
        ], dtype=np.uint8)
    
    clusters = extract_clusters(compat_mat_cluster)

    assert clusters == [[0, 1, 2], [3], [4, 5]]

def test_all():
    compat_mat = np.array([
        [1,1,1,1,1,1,1,0,0,0,0],
        [1,1,1,1,0,0,0,1,0,0,0],
        [1,1,1,1,0,0,0,0,1,0,0],
        [1,1,1,1,0,0,0,1,0,0,0],
        [1,0,0,0,1,1,1,0,0,0,0],
        [1,0,0,0,1,1,1,0,0,0,0],
        [1,0,0,0,1,1,1,0,0,1,0],
        [0,1,0,1,0,0,0,1,1,1,1],
        [0,0,1,0,0,0,0,1,1,1,1],
        [0,0,0,0,0,0,1,1,1,1,1],
        [0,0,0,0,0,0,0,1,1,1,1],
    ])

    clusters = extract_clusters(clusterise_mat(compat_mat))

    assert clusters == [[0], [1,2,3],[4,5,6],[7,8,9,10]]

if __name__ == "__main__":
    import pytest
    pytest.main(["-vv", __file__])