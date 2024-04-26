from utils import proj_geo_to_lambert_delta, proj_lambert_delta_to_geo, format_angle_deg, mean_angles_deg
import pandas as pd
from pytest import approx

def test_proj():
    data = pd.DataFrame([
        ["Paris", 48.866, 2.333], 
        ["Lyon", 45.750, 4.850], 
        ["Toulouse", 43.600, 1.433]
    ], columns=("ville", "lat", "lng"))
    proj_geo_to_lambert_delta(data, delta=[0,0])

    assert abs(data.loc[0].e-651069.12) + abs(data.loc[0].n-6863092.19) < 1

    data.loc[:, "lat"] = 0
    data.loc[:, "lng"] = 0
    proj_lambert_delta_to_geo(data, delta=[0,0])
    assert abs(data.loc[0].lat-48.866) + abs(data.loc[0].lng-2.333) < 0.01


def test_format_angle():
    assert format_angle_deg(0) == 0
    assert format_angle_deg(-180) == 180
    assert format_angle_deg(90) == 90
    assert format_angle_deg(360) == 0
    assert format_angle_deg(270) == -90
    assert format_angle_deg(-90) == -90


def test_mean_angle():
    assert mean_angles_deg([0, 5]) == approx(2.5)
    assert mean_angles_deg([-175, 165]) == approx(175)

if __name__ == "__main__":
    import pytest
    pytest.main(["-v", __file__])