from main_clusterize import appareille_list, appareille_panneaux
import pandas as pd

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
            [None, 30, 20, 1.2,   0, "C", None],
            [None, 40, 50, 1.1, -90, "D", None],
            [None, 20,  0, 0.8, 180, "B", None],
            [None, 10, 10, 1.0, -90, "A", None],
            [None, 20,  0, 2.8, 180, "B", None],
            [None, 30, 50, 1.2,   0, "C", None],
            [None, 40, 51, 1.1,  90, "D", None],
        ], columns=("id", "e", "n", "size", "orientation", "code", "value")
    )
    panneaux_c = pd.DataFrame([
            [1, 10, 10, 1.0,  90, "A", None],
            [2, 20,  0, 0.8, 180, "B", None],
            [3, 30, 20, 1.2,   0, "C", None],
            [4, 40, 50, 1.1, -90, "D", None],
        ], columns=("id", "e", "n", "size", "orientation", "code", "value")
    )
    links = appareille_panneaux(panneaux_d, panneaux_c)

    assert links == [(0, 2), (1, 3), (2, 1)]

if __name__ == "__main__":
    import pytest
    pytest.main(["-v", __file__])