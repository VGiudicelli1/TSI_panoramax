from main_clusterize import appareille_list, appareille_panneaux, compute_panneaux, update_detection_fk_id, save_new_panneaux, save_detections, load
import pandas as pd
import numpy as np
from database_connect import connect_db

def test_appareille_list():
    l1 = [1, 4, 7, 9]
    l2 = [5, 10, 6, 0]
    dist = lambda x, y: abs(x-y)

    links = appareille_list(l1, l2, dist)

    assert links == [(0,3), (1,0), (2, 2), (3,1)]

def test_appareille_list_inf_dist():
    l1 = [1, 4, 7, 9, 50]
    l2 = [5, 10, 6, 0]

    dist = lambda x, y: abs(x-y) if (x,y) != (9,10) else float("inf")
    links = appareille_list(l1, l2, dist)
    assert links == [(0,3), (1,0), (2, 2)]

    dist = lambda x, y: float("inf")
    links = appareille_list(l1, l2, dist)
    assert links == []

def test_appareille_panneaux():
    panneaux_d = pd.DataFrame([
            [None, 30, 20, 1.2,   0, "C", None, "a"],
            [None, 40, 50, 1.1, -90, "D", None, "b"],
            [None, 20,  0, 0.8, 180, "B", None, "c"],
            [None, 10, 10, 1.0, -90, "A", None, "d"],
            [None, 20,  0, 2.8, 180, "B", None, "e"],
            [None, 30, 50, 1.2,   0, "C", None, "f"],
            [None, 40, 51, 1.1,  90, "D", None, "g"],
        ], columns=("id", "e", "n", "size", "orientation", "code", "value", "temp_id")
    )
    panneaux_c = pd.DataFrame([
            ["1", 10, 10, 1.0,  90, "A", None],
            ["2", 20,  0, 0.8, 180, "B", None],
            ["3", 30, 20, 1.2,   0, "C", None],
            ["4", 40, 50, 1.1, -90, "D", None],
        ], columns=("id", "e", "n", "size", "orientation", "code", "value")
    )
    links = appareille_panneaux(panneaux_d, panneaux_c)

    assert links == [(0, 2), (1, 3), (2, 1)]

    np.testing.assert_array_equal(
        panneaux_d.id,
        ["3", "4", "2", None, None, None, None])

def test_compute_panneaux():
    detections = pd.DataFrame([
        ["000",  0, 40, "B14", "30", -30.0,  116.565051, 11.180340],
        ["001", 40, 40, "B14", "30", -30.0,  -99.462322, 30.413813],
        ["002", 45, 25, "B14", "30", -30.0,  -74.054604, 36.400549],
        ["003", 20,  0, "B14", "30", -30.0,  -15.945396, 36.400549],
        ["000", 40, 40, "B14", "50",  40.0, -126.869898,  8.333333],
        ["001", 45, 25, "B14", "50",  40.0,  -90.000000,  8.333333],
        ["002", 20,  0, "B14", "50",  40.0,    0.000000,  8.333333],
        ["003",  0, 40, "B14", "50",  40.0,  168.690068, 12.747549],
        ["000", 40, 40, "A00", None,  40.0, -126.869898,  8.333333],
        ["001", 45, 25, "A00", None,  40.0,  -90.000000,  8.333333],
        ["002", 20,  0, "A00", None,  40.0,    0.000000,  8.333333],
        ["003",  0, 40, "A00", None,  40.0,  168.690068, 12.747549],
    ], columns=("source_id", "source_E", "source_N", "code", "value", "orientation", "gisement", "sdf"))
    
    clusters = [[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]]

    panneaux = compute_panneaux(detections, clusters)

    assert "panneau_id_temp" in detections.columns
    np.testing.assert_array_equal(panneaux.temp_id, ["a", "b"])
    np.testing.assert_array_equal(
        detections.panneau_id_temp, 
        ["a" , "a" , "a" , "a",
         "b" , "b" , "b" , "b",
         None, None, None, None]
    )

def test_update_fk_panneaux():
    detections = pd.DataFrame([
        ["a"],
        ["a"],
        ["b"],
        ["b"],
        ["b"],
        ["c"],
        ["d"],
        [None],
    ], columns=("panneau_id_temp", ))
    panneaux = pd.DataFrame([
        ["12", "a"],
        ["27", "b"],
        ["48", "c"],
        [None, "d"],
    ], columns=("id", "temp_id"))

    update_detection_fk_id(detections, panneaux)

    assert "panneau_id" in detections.columns
    np.testing.assert_array_equal(
        detections["panneau_id"],
        ["12", "12", "27", "27", "27", "48", None, None]
    )

def test_insert_new_panneaux():
    # this test will insert data into database. Run it manualy on a database for tests
    return
    conn, config = connect_db()
    load(conn)  # loading is necessary to init proj (delta)
    
    panneaux = pd.DataFrame([
            [311, 30, 20, 1.2,   0, "C", None, "a"],
            [120, 40, 50, 1.1, -90, "D", None, "b"],
            [459, 20,  0, 0.8, 180, "B", None, "c"],
            [None, 10, 10, 1.0, -90, "A", None, "d"],
            [None, 20,  0, 2.8, 180, "B", None, "e"],
            [None, 30, 50, 1.2,   0, "C", None, "f"],
            [None, 40, 51, 1.1,  90, "D", None, "g"],
        ], columns=("id", "e", "n", "size", "orientation", "code", "value", "temp_id")
    )
    save_new_panneaux(conn, panneaux)

    assert not panneaux.id.isnull().any()
    assert panneaux.loc[2, "id"] == 459

def test_update_detections():
    # this test will update data into database. Run it manualy on a database for tests
    return
    conn, config = connect_db()
    detections = pd.DataFrame([
        [ "1", "000",  0, 40, "B14", "30", -30.0,  116.565051, 11.180340, "1"],
        [ "2", "001", 40, 40, "B14", "30", -30.0,  -99.462322, 30.413813, "1"],
        [ "3", "002", 45, 25, "B14", "30", -30.0,  -74.054604, 36.400549, "1"],
        [ "4", "003", 20,  0, "B14", "30", -30.0,  -15.945396, 36.400549, "1"],
        [ "5", "000", 40, 40, "B14", "50",  40.0, -126.869898,  8.333333, "2"],
        [ "6", "001", 45, 25, "B14", "50",  40.0,  -90.000000,  8.333333, "2"],
        [ "7", "002", 20,  0, "B14", "50",  40.0,    0.000000,  8.333333, "2"],
        [ "8", "003",  0, 40, "B14", "50",  40.0,  168.690068, 12.747549, "2"],
        [ "9", "000", 40, 40, "A00", None,  40.0, -126.869898,  8.333333, "3"],
        ["10", "001", 45, 25, "A00", None,  40.0,  -90.000000,  8.333333, "3"],
    ], columns=("id", "source_id", "source_E", "source_N", "code", "value", "orientation", "gisement", "sdf", "panneau_id"))
    save_detections(conn, detections)

if __name__ == "__main__":
    import pytest
    pytest.main(["-v", __file__])