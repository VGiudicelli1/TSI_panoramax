import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from algo_infos_panneaux import extraction as extraction
from algo_infos_panneaux import trouver_centre_panneau as trouver_centre_panneau
import cv2

dico = trouver_centre_panneau.csv_reader('useful_data/data_doc/panodico.csv')

def test_get_whxy():
	assert extraction.get_whxy_from_img_path('useful_data/data_test/test_A14.jpg') == (11000, 5500, 544, 2384)
	assert extraction.get_whxy_from_img_path('useful_data/data_test/test_B14.jpg') == (11000, 5500, 5952, 2720)
	assert extraction.get_whxy_from_img_path('useful_data/data_test/test_C12.jpg') == (11000, 5500, 7856, 2480)

def test_get_shape():	
	img = cv2.imread('useful_data/data_test/test_A14.jpg')
	gray = trouver_centre_panneau.BGRtoGRAY(img)
	edges = trouver_centre_panneau.DetectionContours(gray)
	shape = trouver_centre_panneau.get_shape('A14',dico)
	assert shape == 0

	img = cv2.imread('useful_data/data_test/test_B14.jpg')
	gray = trouver_centre_panneau.BGRtoGRAY(img)
	edges = trouver_centre_panneau.DetectionContours(gray)
	shape = trouver_centre_panneau.get_shape('B14',dico)
	assert shape == 4

	img = cv2.imread('useful_data/data_test/test_C12.jpg')
	gray = trouver_centre_panneau.BGRtoGRAY(img)
	edges = trouver_centre_panneau.DetectionContours(gray)
	shape = trouver_centre_panneau.get_shape('C12',dico)
	assert shape == 5

def test_find_center_in_original_picture():
	#Testing Triangle Shape
	img = cv2.imread('useful_data/data_test/test_A14.jpg')
	imgGray = trouver_centre_panneau.BGRtoGRAY(img)
	imgEdges = trouver_centre_panneau.DetectionContours(imgGray)
	shape = trouver_centre_panneau.get_shape('A14', dico)
	contour,sides = trouver_centre_panneau.get_contour(img,imgEdges,shape)
	center_in_cropped = trouver_centre_panneau.get_center_in_cropped_sign(img, shape, imgEdges, contour,sides)
	w,h,x,y = extraction.get_whxy_from_img_path('useful_data/data_test/test_A14.jpg')
	final_center = trouver_centre_panneau.find_center_in_original_picture(img, center_in_cropped, x, y)
	real_center = (659,2529)
	assert(final_center[0] > (real_center[0]-10) & final_center[0] < (real_center[0] + 10))
	assert(final_center[1] > (real_center[1]-10) & final_center[1] < (real_center[1] + 10))
	
	#Testing Circle Shape
	img = cv2.imread('useful_data/data_test/test_B14.jpg')
	imgGray = trouver_centre_panneau.BGRtoGRAY(img)
	imgEdges = trouver_centre_panneau.DetectionContours(imgGray)
	shape = trouver_centre_panneau.get_shape('B14',dico)
	contour,sides = trouver_centre_panneau.get_contour(img,imgEdges,shape)
	center_in_cropped = trouver_centre_panneau.get_center_in_cropped_sign(img,shape,imgEdges,contour,sides)
	w,h,x,y = extraction.get_whxy_from_img_path('useful_data/data_test/test_B14.jpg')
	final_center = trouver_centre_panneau.find_center_in_original_picture(img, center_in_cropped,x,y)
	real_center = (5999,2786)
	assert(final_center[0] > (real_center[0]-10) & final_center[0] < (real_center[0] + 10))
	assert(final_center[1] > (real_center[1]-10) & final_center[1] < (real_center[1] + 10))

	#Testing Square Shape
	img = cv2.imread('useful_data/data_test/test_C12.jpg')
	imgGray = trouver_centre_panneau.BGRtoGRAY(img)
	imgEdges = trouver_centre_panneau.DetectionContours(imgGray)
	shape = trouver_centre_panneau.get_shape('C12',dico)
	contour,sides = trouver_centre_panneau.get_contour(img,imgEdges,shape)
	center_in_cropped = trouver_centre_panneau.get_center_in_cropped_sign(img,shape,imgEdges,contour,sides)
	w,h,x,y = extraction.get_whxy_from_img_path('useful_data/data_test/test_C12.jpg')
	final_center = trouver_centre_panneau.find_center_in_original_picture(img, center_in_cropped,x,y)
	real_center = (7955,2588)
	assert(final_center[0] > (real_center[0]-10) & final_center[0] < (real_center[0] + 10))
	assert(final_center[1] > (real_center[1]-10) & final_center[1] < (real_center[1] + 10))
	
if __name__ == "__main__":
	import pytest
	pytest.main(["-v", __file__])
