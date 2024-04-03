import extraction
import trouver_centre_panneau
import cv2

def test_get_whxy():
    assert extraction.get_whxy_from_img_path('data_test/test_A14.jpg') == (11000, 5500, 544, 2384)
    assert extraction.get_whxy_from_img_path('data_test/test_B14.jpg') == (11000, 5500, 5952, 2720)
    assert extraction.get_whxy_from_img_path('data_test/test_C12.jpg') == (11000, 5500, 4208, 2672)

def test_get_shape():    
    img = cv2.imread('data_test/test_A14.jpg')
    gray = trouver_centre_panneau.BGRtoGRAY(img)
    edges = trouver_centre_panneau.DetectionContours(gray)
    shape = trouver_centre_panneau.get_shape('A14')
    assert shape == 0

    img = cv2.imread('data_test/test_B14.jpg')
    gray = trouver_centre_panneau.BGRtoGRAY(img)
    edges = trouver_centre_panneau.DetectionContours(gray)
    shape = trouver_centre_panneau.get_shape('B14')
    assert shape == 4

    img = cv2.imread('data_test/test_C12.jpg')
    gray = trouver_centre_panneau.BGRtoGRAY(img)
    edges = trouver_centre_panneau.DetectionContours(gray)
    shape = trouver_centre_panneau.get_shape('C12')
    assert shape == 5

def test_find_center_in_original_picture():
    img = cv2.imread('data_test/test_A14.jpg')
    imgGray = trouver_centre_panneauBGRtoGRAY(img)
    imgEdges = trouver_centre_panneauDetectionContours(imgGray)
    shape = trouver_centre_panneauget_shape(tag, dico)
    center_in_cropped = trouver_centre_panneauget_center_in_cropped_sign(img, 'A14', imgEdges)
    w,h,x,y = extraction.get_whxy_from_img_path(photo_path)
    final_center = trouver_centre_panneaufind_center_in_original_picture(img, center_in_cropped, x, y)
    real_center = (659,2529)
    assert(final_center[0] > (real_center[0]-20) & final_center[0] < (real_center[0] + 20))
    assert(final_center[1] > (real_center[1]-20) & final_center[1] < (real_center[1] + 20))
	    
if __name__ == "__main__":
    import pytest
    pytest.main(["-v", __file__])
