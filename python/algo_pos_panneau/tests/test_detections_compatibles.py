import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from algo_pos_panneau.detections_compatible import are_detections_compatibles, are_orientations_compatibles, are_positions_compatibles, compatible_matrix
import pandas as pd
import numpy as np


def make_binary_matrix(df, fonc):
    n = len(df)
    index = list(df.index)
    return np.array(
        [[
            fonc(df.loc[df.index.isin([index[i], index[j]])]) 
            for i in range(n)] 
            for j in range(n) 
        ], dtype=np.uint8)


def make_dataset(noise = 0):
    data = pd.DataFrame([
        ["000",  0, 40, "B14", "30", -30.0,  116.565051, 11.180340],
        ["001", 40, 40, "A00", None, -30.0,  -99.462322, 30.413813],
        ["002", 45, 25, "A00", None, -30.0,  -74.054604, 36.400549],
        ["003", 20,  0, "A00", None, -30.0,  -15.945396, 36.400549],
        ["001", 40, 40, "B14", "30",  40.0, -126.869898,  8.333333],
        ["002", 45, 25, "B14", "30",  40.0,  -90.000000,  8.333333],
        ["003", 20,  0, "A00", None,  40.0,    0.000000,  8.333333],
        ["000",  0, 40, "A00", None, 160.0,  168.690068, 12.747549],
        ["001", 40, 40, "A00", None, 160.0, -125.537678, 21.505813],
        ["002", 45, 25,  "B1", None, 160.0, -104.036243, 20.615528],
        ["003", 20,  0,  "B1", None, 160.0,  -45.000000, 10.606602],
    ], columns=("source_id", "source_E", "source_N", "code", "value", "orientation", "gisement", "sdf"))

    size = len(data)
    data.source_E    += np.random.normal(loc=0, scale=0.5*noise, size=size)
    data.source_N    += np.random.normal(loc=0, scale=0.5*noise, size=size)
    data.orientation += np.random.normal(loc=0, scale=0.2*noise, size=size)
    data.gisement    += np.random.normal(loc=0, scale=0.2*noise, size=size)
    data.sdf         *= np.random.normal(loc=1, scale=0.1*noise, size=size)

    return data


def test_compatible_unique_detection():
    detections = make_dataset(0)
    assert     are_detections_compatibles(detections.loc[detections.index.isin([0])])
    assert     are_detections_compatibles(detections.loc[detections.index.isin([4])])
    assert     are_detections_compatibles(detections.loc[detections.index.isin([7])])


def test_compatible_source():
    detections = pd.DataFrame([
        ["000",  0, 40, "B14", "30", -30.0,  116.565051, 11.180340],
        ["001",  0, 40, "B14", "30", -30.0,  116.565051, 11.180340],
        ["000",  0, 40, "B14", "30", -30.0,  116.565051, 11.180340],
    ], columns=("source_id", "source_E", "source_N", "code", "value", "orientation", "gisement", "sdf"))

    assert     are_detections_compatibles(detections.loc[detections.index.isin([0, 1])])
    assert not are_detections_compatibles(detections.loc[detections.index.isin([0, 2])])


def test_compatible_code_face(): 
    detections = pd.DataFrame([
        ["000",  0, 40, "B14", "30", -30.0,  116.565051, 11.180340],
        ["001",  0, 40, "B12", "30", -30.0,  116.565051, 11.180340],
        ["002",  0, 40, "B14", "30", -30.0,  116.565051, 11.180340],
    ], columns=("source_id", "source_E", "source_N", "code", "value", "orientation", "gisement", "sdf"))

    assert not are_detections_compatibles(detections.loc[detections.index.isin([0, 1])])
    assert     are_detections_compatibles(detections.loc[detections.index.isin([0, 2])])


def test_compatible_code_face_back(): 
    detections = pd.DataFrame([
        ["000",  0, 40, "B14", "30", -30.0,  116.565051, 11.180340],
        ["001",  0, 40, "A00", "30", -30.0,  116.565051, 11.180340],
        ["002",  0, 40, "B12", "30", -30.0,  116.565051, 11.180340],
        ["003",  0, 40, "A00", "30", -30.0,  116.565051, 11.180340],
    ], columns=("source_id", "source_E", "source_N", "code", "value", "orientation", "gisement", "sdf"))

    assert     are_detections_compatibles(detections.loc[detections.index.isin([0, 1])])
    assert     are_detections_compatibles(detections.loc[detections.index.isin([1, 2])])
    assert     are_detections_compatibles(detections.loc[detections.index.isin([2, 3])])

    assert     are_detections_compatibles(detections.loc[detections.index.isin([0, 1, 3])])
    assert not are_detections_compatibles(detections.loc[detections.index.isin([0, 2])])
    assert     are_detections_compatibles(detections.loc[detections.index.isin([1, 2, 3])])


def test_compatible_value(): 
    detections = pd.DataFrame([
        ["000",  0, 40, "B14", "30", -30.0,  116.565051, 11.180340],
        ["001",  0, 40, "B14", "30", -30.0,  116.565051, 11.180340],
        ["002",  0, 40, "B14", "10", -30.0,  116.565051, 11.180340],
        ["003",  0, 40, "B14", None, -30.0,  116.565051, 11.180340],
        ["004",  0, 40, "A00", None, -30.0,  116.565051, 11.180340],
    ], columns=("source_id", "source_E", "source_N", "code", "value", "orientation", "gisement", "sdf"))

    assert     are_detections_compatibles(detections.loc[detections.index.isin([0, 1])])
    assert not are_detections_compatibles(detections.loc[detections.index.isin([0, 2])])
    assert not are_detections_compatibles(detections.loc[detections.index.isin([0, 3])])
    assert     are_detections_compatibles(detections.loc[detections.index.isin([0, 4])])


def test_compatible_orientation():
    detections = pd.DataFrame([
        ["001",  0, 40, "B14", "30",   90, -30.0, 11.180340],    # E
        ["002",  0, 40, "B14", "30",  180, -30.0, 11.180340],    # S
        ["000",  0, 40, "B14", "30",    0, -30.0, 11.180340],    # N
        ["003",  0, 40, "B14", "30",  -90, -30.0, 11.180340],    # W
        ["004",  0, 40, "B14", "30",  270, -30.0, 11.180340],    # W
        ["005",  0, 40, "B14", "30",  360, -30.0, 11.180340],    # N
        ["005",  0, 40, "B14", "30", -180, -30.0, 11.180340],    # S
        ["004",  0, 40, "B14", "30", -270, -30.0, 11.180340],    # E
    ], columns=("source_id", "source_E", "source_N", "code", "value", "orientation", "gisement", "sdf"))
    
    bmat = make_binary_matrix(detections, are_orientations_compatibles)
    np.testing.assert_array_equal(
        bmat,
        [[1, 0, 0, 0, 0, 0, 0, 1],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [0, 0, 1, 0, 0, 1, 0, 0],
         [0, 0, 0, 1, 1, 0, 0, 0],
         [0, 0, 0, 1, 1, 0, 0, 0],
         [0, 0, 1, 0, 0, 1, 0, 0],
         [0, 1, 0, 0, 0, 0, 1, 0],
         [1, 0, 0, 0, 0, 0, 0, 1]])


def test_compatible_position():
    detections = pd.DataFrame([
        ["001", 10, 10, "B14", None, 0,   0, 30],    # pt1, N, 30m pour 1m  (s:1m)
        ["002", 40, 40, "B14", None, 0, -90, 30],    # pt2, W, 30m pour 1m  (s:1m)
        ["001", 10, 10, "B14", None, 0,  90, 10],    # pt1, E, 10m pour 1m  (s:3m)
        ["002", 40, 40, "B14", None, 0, 180, 10],    # pt2, S, 10m pour 1m  (s:3m)
        ["001", 10, 10, "B14", None, 0,   0, 10],    # pt1, N, 10m pour 1m  (s:3m)
        ["002", 40, 40, "B14", None, 0, -90, 10],    # pt2, W, 10m pour 1m  (s:3m)
        ["001", 10, 10, "B14", None, 0,  90, 20],    # pt1, E, 20m pour 1m  (s:1.6m)
        ["002", 40, 40, "B14", None, 0, 180, 20],    # pt2, S, 20m pour 1m  (s:1.6m)
    ], columns=("source_id", "source_E", "source_N", "code", "value", "orientation", "gisement", "sdf"))
    
    # note: compatible quand meme pt et size = 0: ce cas est différencié par le critére de différence de source
    bmat = make_binary_matrix(detections, are_positions_compatibles)
    np.testing.assert_array_equal(
        bmat,
        [[1, 1, 1, 0, 1, 0, 1, 0],
         [1, 1, 0, 1, 0, 1, 0, 1],
         [1, 0, 1, 1, 1, 0, 1, 0],
         [0, 1, 1, 1, 0, 1, 0, 1],
         [1, 0, 1, 0, 1, 1, 1, 0],
         [0, 1, 0, 1, 1, 1, 0, 1],
         [1, 0, 1, 0, 1, 0, 1, 1],
         [0, 1, 0, 1, 0, 1, 1, 1]])


def test_compatible_matrix():
    detections = make_dataset(0)

    # test without orientation
    detections.loc[:, "orientation"] = 0
    
    compat_mat, index, rindex = compatible_matrix(detections)
    compat_mat_2 = np.array([
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

    np.testing.assert_array_equal(
        compat_mat,
        compat_mat_2
        )


if __name__ == "__main__":
    import pytest
    pytest.main(["-v", __file__])
