from compute_cropped_measurments import compute
import pandas as pd
from pytest import approx


def test_compute_create_columns():
    data = pd.DataFrame([
        [54,   372.0,  1442.0,  35.0,          5760,           2880,       360.0,          354.0],
        [55,   652.0,  1392.0,  83.0,          5760,           2880,       360.0,            1.0],
    ], columns=("id", "x", "y", "dz", "source_width", "source_height", "source_fov", "source_azimut"))

    compute(data)

    assert "id" in data.columns
    assert "sdf" in data.columns
    assert "gisement" in data.columns

def test_compute_create_columns_if_empty():
    data = pd.DataFrame([
    ], columns=("id", "x", "y", "dz", "source_width", "source_height", "source_fov", "source_azimut"))

    compute(data)

    assert "id" in data.columns
    assert "sdf" in data.columns
    assert "gisement" in data.columns

def test_compute_result_gisement():
    data = pd.DataFrame([
        [0,   500,  500,  10,          1000, 1000,      360.0,          21.3],
        [1,   250,  500,  20,          1000, 1000,      360.0,          21.3],
        [2,  1000,  500,  30,          1000, 1000,      360.0,          21.3],
    ], columns=("id", "x", "y", "dz", "source_width", "source_height", "source_fov", "source_azimut")
    )

    compute(data)

    assert data.loc[0, "gisement"] == 21.3
    assert data.loc[1, "gisement"] == 21.3-90
    assert data.loc[2, "gisement"] == 21.3+180

def test_compute_result_sdf():
    data = pd.DataFrame([
        [0,   500,  500,  10,          1000, 1000,      360.0,          21.3],
        [1,   250,  500,  20,          1000, 1000,      360.0,          21.3],
        [2,  1000,  500,  30,          1000, 1000,      360.0,          21.3]
    ], columns=("id", "x", "y", "dz", "source_width", "source_height", "source_fov", "source_azimut"))

    compute(data)

    assert data.loc[0, "sdf"] == approx(16, abs=0.1)
    assert data.loc[1, "sdf"] == approx(8, abs=0.1)
    assert data.loc[2, "sdf"] == approx(5.3, abs=0.1)


if __name__ == "__main__":
    import pytest
    pytest.main(["-v", __file__])