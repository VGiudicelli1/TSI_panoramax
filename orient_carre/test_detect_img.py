from find_motif import *
import pytest
import numpy as np

__path__ = "/".join(__file__.split("/")[:-1])

def test_find_motif():
    img = Image.open(__path__ + "/C28_detecte.jpg").convert("RGB")
    assert img.size == (112, 160)
    
    motif = img.crop([0, 0, 20, 20])
    x, y, corr = find_motif(img, motif)
    assert (x, y) == (10, 10)

    motif = img.crop([20, 50, 40, 70])
    x, y, corr = find_motif(img, motif)
    assert (x, y) == (30, 60)

def test_find_motif_speed():
    img = Image.open(__path__ + "/C28_detecte.jpg").convert("RGB")
    
    motif = img.crop([0, 0, 20, 20])
    x, y, corr = find_motif_speed(img, motif, 32) # equivalent size of searched motif: 6x6 px
    np.testing.assert_array_almost_equal(
        (x, y),
        (10, 10),
        0
    )

    motif = img.crop([20, 50, 40, 70])
    x, y, corr = find_motif_speed(img, motif, 40)  # 14x14 px in motif
    np.testing.assert_array_almost_equal(
        (x, y),
        (30, 60),
        0
    )

def test_arange():
    np.testing.assert_array_equal(
        arange(1, 5, 5),
        [1, 2, 3, 4, 5]
    )

    np.testing.assert_array_equal(
        arange(1, 5, 9),
        [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5]
    )

def test_find_motif_scale():
     
    img = Image.open(__path__ + "/C28_detecte.jpg").convert("RGB")
    
    motif = img.crop([0, 0, 20, 20]).resize((10, 10))
    x, y, dz, corr = find_motif_scale(img, motif, dz_rel_min=0.5, dz_rel_max=3, dz_steps=6, rel_from_img=False)
    assert dz==20

if __name__ == "__main__":
    test_arange()
    test_find_motif_scale()
    