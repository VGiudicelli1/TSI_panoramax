import extraction
import moteur
import cv2

def test_get_whxy():
    assert extraction.get_whxy_from_img_path('data_test/test_A14.jpg') == (11000, 5500, 544, 2384)
    assert extraction.get_whxy_from_img_path('data_test/test_B14.jpg') == (11000, 5500, 5952, 2720)
    assert extraction.get_whxy_from_img_path('data_test/test_C12.jpg') == (11000, 5500, 4208, 2672)

def test_find_sign():    
    img = cv2.imread('data_test/test_A14.jpg')
    gray = moteur.BGRtoGRAY(img)
    edges = moteur.DetectionContours(gray)
    shape,contour = moteur.find_sign(img,edges)
    assert shape == 'triangle'

    img = cv2.imread('data_test/test_B14.jpg')
    gray = moteur.BGRtoGRAY(img)
    edges = moteur.DetectionContours(gray)
    shape,contour = moteur.find_sign(img,edges)
    assert shape == 'cercle'

    img = cv2.imread('data_test/test_C12.jpg')
    gray = moteur.BGRtoGRAY(img)
    edges = moteur.DetectionContours(gray)
    shape,contour = moteur.find_sign(img,edges)
    #assert shape == 'carre'

if __name__ == "__main__":
    import pytest
    pytest.main(["-v", __file__])