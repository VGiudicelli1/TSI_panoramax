import pandas as pd
import pytest
import numpy as np
from main_recompute_sign import recompute_all_signs

def test_recompute_sign():
    signs = pd.DataFrame([
        ["107", 10013.0, 20016.0, 1.0,   0.0, -1.0, "B14", "30"],
        ["294", 10059.0, 20005.0, 0.8, -37.0, -1.0, "B14", "50"],
        ["741", 10021.0, 20082.0, 1.2,  98.0, -1.0, "B14", "70"],
    ], columns=("id", "e", "n", "size", "orientation", "precision", "code", "value"))
    
    cropped_signs = pd.DataFrame([
        ["952", 10053.0, 10026.0, "107", 30.0, -135.0,  -7.0, "B14", "30"],
        ["953", 10053.0, 10026.0, "294", 20.0, -175.0, -47.0, "B14", "50"],
        ["954", 10053.0, 10026.0, "741", 20.0,  -45.0,  94.0, "B14", "70"],
        ["955", 10012.0, 10049.0, "107", 30.0,  175.0,   7.0, "B14", "30"],
        ["956", 10012.0, 10049.0, "294", 40.0,  135.0, -27.0, "B14", "50"],
        ["957", 10012.0, 10049.0, "741", 35.0,   80.0, 100.0, "B14", "70"],
    ], columns=("id", "e", "n", "sign_id", "sdf", "gisement", "orientation", "code", "value"))

    recompute_all_signs(signs, cropped_signs)

    np.testing.assert_array_almost_equal(
        signs.orientation,
        [0, -37, 97],
        1
    )

    np.testing.assert_array_almost_equal(
        signs["size"],
        [1.8, 1.4, 0.9],
        1
    )

    np.testing.assert_array_almost_equal(
        signs.e,
        [10015.5, 10052, 10041.5],
        1
    )

if __name__ == "__main__":
    import pytest

    test_recompute_sign()

    pytest.main(["-v", __file__])