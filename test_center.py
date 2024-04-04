import extraction
import trouver_centre_panneau

def test_get_whxy():
    assert get_whxy_from_img_path('test_A14.jpg') == (11000, 5500, 5440, 2384)
    assert get_whxy_from_img_path('testB14.jpg') == (11000, 5500, 5952, 2720)
    assert get_whxy_from_img_path('test_C12.jpg') == (11000, 5500, 7104, 2416)

def test_find_sign():
    shape,contour = find_sign('test_A14.jpg')
    assert shape == 'triangle'
    shape,contour = find_sign('test_B14.jpg')
    assert shape == 'cercle'
    shape,contour = find_sign('test_C12.jpg')
    assert shape == 'carre'
    
if __name__ == "__main__":
    import pytest
    pytest.main(["-v", __file__])
