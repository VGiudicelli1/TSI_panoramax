from find_motif import *
import pytest
import numpy as np

def test_find_motif():
    img = Image.open("C28_detecte.jpg").convert("RGB")
    assert img.size == (112, 160)
    
    motif = img.crop([0, 0, 20, 20])
    x, y, corr = find_motif(img, motif)
    assert (x, y) == (10, 10)

    motif = img.crop([20, 50, 40, 70])
    x, y, corr = find_motif(img, motif)
    assert (x, y) == (30, 60)

def test_find_motif_speed():
    img = Image.open("C28_detecte.jpg").convert("RGB")
    
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

def test_find_motif_scale():
    img = Image.open("C28_detecte.jpg").convert("RGB")
    
    motif = img.crop([0, 0, 20, 20]).resize((10, 10))
    x, y, dz, corr = find_motif_scale(img, motif)
    assert dz==20

if __name__ == "__main__":
    pass