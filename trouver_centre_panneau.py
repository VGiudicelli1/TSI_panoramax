#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  3 13:47:15 2024

@author: Victorien
"""

###### 0 - Imports #####

import numpy as np
import cv2
import math
import plotting
import extraction
import pandas as pd
import os
from scipy.spatial import ConvexHull

def csv_reader(path):
	"""
	Read a csv file and makes it a dictionnary

	Parameters
	----------
	path : String
		Path of .csv file.

	Returns 
	-------
	TYPE : Dictionnary
		Associates each sign code to a number between 0 and 9, correspondin to the sign shape

	"""
	return dict(np.genfromtxt(path, delimiter=",", dtype=None, encoding='UTF8'))


def BGRtoGRAY(img):
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	return gray


def DetectionContours(imgGray):
	imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 0)
	edges = cv2.Canny(imgBlur, 50, 150)
	return edges


def get_shape(tag, dico):
	"""
	Returns the shape of the sign in the cropped image, with a code systemm
	(exemple : 0 = triangle, 2 = octogon, etc)

	Parameters
	----------
	tag : String
		Code of the sign in the original nomenclature.
	dico : dict
		Dictionnary associating to a tag a code symbolizing its shape.

	Returns
	-------
	TYPE : int
		Code symbolizing the sign shape.

	"""
	return dico[tag]


def get_contour(img, edges, shape):
	"""
	This function returns the biggest closed contour found in the cropped sign,
	considered so as the sign contour

	Parameters
	----------
	img : ndarray
		Cropped sign image.
	edges : ndarray
		Canny contours detected in img.
	shape : int
		Code symbolizing the shape of the sign in the imge

	Returns
	-------
	approx : ndarray
		Approximation of the largest polygon on the image.
	sides : int
		Number of sides of the polygon approximated on the biggest contour detected.

	"""
	# On attribue une valeur de epsilon pour cibler au mieux une recherche de forme
	if shape == 2 or shape == 4: # Circle and Octogon
		value_for_epsilon = 0.02
	elif shape == 0 or shape ==1 or shape == 9 : # Triangle
		value_for_epsilon = 0.15
	else:
		value_for_epsilon = 0.15
	# Finding contours in the image
	contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	# Sorting them to get the biggest one
	contours = sorted(contours, key=cv2.contourArea, reverse=True)
	largest_contour = contours[0]
	
	# Approximation of a polygon
	epsilon = value_for_epsilon * cv2.arcLength(largest_contour, True) # Definition of the factor 
	approx = cv2.approxPolyDP(largest_contour, epsilon, True) # Approximation
	sides = len(approx) # Number of sides of the polygon, to know if we found the good form
	# x_min, x_max, y_min, y_max = which_circle(img, largest_contour)
	#cv2.drawContours(img, [largest_contour], -1, (0, 255, 0), 2)
	#cv2.drawContours(img, [approx], -1, (255, 0, 0), 2)
	return approx, sides



def get_center_in_cropped_sign(img, shape, imgEdges, contour_sign, number_of_sides):
	"""
	This function returns the center of the sign in the cropped image.
	It does have a role of a processing function.

	Parameters
	----------
	img : ndarray
		Image of the cropped sign.
	shape : int
		Code to signify the shape of the sign in the image.
	imgEdges : ndarray
		Canny contours detected in the cropped sign image.
	contour_sign : ndarray
		list of the points constituing the contour of the sign.
	number_of_sides : int
		Number of sides detectedof the polygon

	Returns
	-------
	center_sign : tuple
		Center of the sign in the cropped image

	"""
	if shape == 0: ## Triangle-top case
		if number_of_sides != 3: # If the number of sides is not corresponding to the hoped shape ...
			center_sign = None # ... We just take the center of the cropped sign
		else:
			center_sign = get_center_triangle(img, contour_sign, True) # Or we search the center of the sign (to the top)
			
	elif shape == 1 or shape == 9: ## Triangle-bottom case
		if number_of_sides != 3: # If the number of sides is not corresponding to the hoped shape ...
			center_sign = None # ...  We just take the center of the cropped sign
		else:
			center_sign = get_center_triangle(img, contour_sign, False) # Or we search the center of the sign (to the bottom)
	
	elif shape == 2 :## Octogon case
		if number_of_sides != 8: # If the number of sides is not corresponding to the hoped shape ...
			center_sign = None # ... We just take the center of the cropped sign
		else:
			center_sign = get_center_circle(img, contour_sign) #  Or we search the cneter of the sign (Octogon)
	elif shape == 3 or shape== 5 or shape == 6 or shape == 7 or shape == 8:## Rectangle case
		if number_of_sides != 4: # If the number of sides is not corresponding to the hoped shape ...
			center_sign = None # ... We just take the center of the cropped sign
		else:
			center_sign = get_center_rectangle(img, contour_sign) # Or we search the center of the sign (to the bottom)
	else: ## Circle or unrecognized shape case
		center_sign = get_center_circle(img, contour_sign)
	return center_sign


def get_image_center(img):
	"""
	Function that returns the center of the cropped image,
	useful in the case of a not found sign contour.
	
	Parameters
	----------
	img : ndarray
		Cropped image of the sign

	Returns
	-------
	center : tuple
		Center of the cropped image, not of the sign.

	"""
	height, width = img.shape[:2]
	center_x = width // 2
	center_y = height // 2
	return (center_x, center_y)

def get_center_triangle(img, contour_sign, boolean):
	"""
	This function returns the center of a triangle detected in an image

	Parameters
	----------
	img : ndarray
		Cropped image of the sign.
	contour_sign : ndarray
		list of the points constituing the contour of the sign.
	boolean : bool
		Signify the orientation of the sign : to the top or to the bottom.

	Returns
	-------
	center : tuple
		center of the sign.

	"""
	list_pixels = make_liste_contour(contour_sign) # Formatting function
	
	# We get the coords of the vertex of the triangle
	coord_x_min = min(list_pixels, key=lambda coord: coord[0])
	coord_x_max = max(list_pixels, key=lambda coord: coord[0])
	# The third vertex depends on the orientation of the sign
	if boolean == True:
		coord_y_min = min(list_pixels, key=lambda coord: coord[1])
	elif boolean == False:
		coord_y_min = max(list_pixels, key=lambda coord: coord[1])
	
	# We calculate the center of the sign
	x = math.ceil((coord_x_min[0] + coord_x_max[0] + coord_y_min[0])/3)
	y = math.ceil((coord_x_min[1] + coord_x_max[1] + coord_y_min[1])/3)
	center = (x,y)

	plotting.show_image_triangle(img, coord_x_min, coord_x_max, coord_y_min, center)
	return center

def get_center_circle(img, contour):
	"""
	This function returns the center of a circle detected in an image

	Parameters
	----------
	img : ndarray
		Cropped image of the sign.
	contour : ndarray
		list of the points constituing the contour of the sign.

	Returns
	-------
	center : tuple
		center of the sign.

	"""
	list_x = []
	list_y = []
	for point in contour:
		point = point[0]
		list_x.append(point[0])
		list_y.append(point[1])
	mean_x = math.ceil(np.mean(list_x))
	mean_y = math.ceil(np.mean(list_y))
	center = (mean_x,mean_y)
	cv2.circle(img, center, 1, (0, 255, 0), -1)
	#plotting.show_image(img, title='Objects Detected')
	return center

def get_center_rectangle(img, contour):
	"""
	This function returns the center of a rectangle detected in an image

	Parameters
	----------
	img : ndarray
		Cropped image of the sign.
	contour : ndarray
		list of the points constituing the contour of the sign.

	Returns
	-------
	center : tuple
		center of the sign.

	"""
	list_pixels = make_liste_contour(contour)
	# Getting vertex of the rectangle
	coord_x_min = min(list_pixels, key=lambda coord: coord[0])
	coord_x_max = max(list_pixels, key=lambda coord: coord[0])
	coord_y_min = min(list_pixels, key=lambda coord: coord[1])
	coord_y_max = max(list_pixels, key=lambda coord: coord[1])
	
	x = math.ceil((coord_x_min[0] + coord_x_max[0] + coord_y_min[0] + coord_y_max[0])/4)
	y = math.ceil((coord_x_min[1] + coord_x_max[1] + coord_y_min[1] + coord_y_max[1])/4)
	center = (x,y)
	# Getting the corners
	corners = []
	corners.append(coord_x_min)
	corners.append(coord_x_max)
	corners.append(coord_y_min)
	corners.append(coord_y_max)
	plotting.show_image_rectangle(img, corners, center)
	
	return center
	
def find_center_in_original_picture(img, center, x, y):
	"""
	Function that returns the center of the sign, not in the
	cropped image but in the original picture from the
	Panoramax API

	Parameters
	----------
	img : np.ndarray
		Original image of the sign.
	center : tuple
		Center of the sign calculated, in the cropped image.
	x : int
		Top left of the corner in the original image containing it.
	y : int
		Top left of the corner in the original image containing it.

	Returns
	-------
	final_center : tuple
		Center of the sign in the original image

	"""
	final_x = x + center[0]
	final_y = y + center[1]
	return (final_x,final_y)


def make_liste_contour(contour):
	'''
	Formatting function making a contour, which is a ndarray, a 
	list more easy to deals with.
	

	Parameters
	----------
	contour : np.ndarray
		Closed polygon.

	Returns
	-------
	liste_pixels : list
		list of points constituing the polygon.

	'''
	list_pixels =[]
	for pixel in contour:
		x = pixel[0][0]
		y = pixel[0][1]
		coord = (x,y)
		list_pixels.append(coord)
	return list_pixels


def get_sign_height(img, contour, shape, tag):
	"""

	Parameters
	----------
	img : ndarray
		Cropped image containing the sign.
	contour : ndarray
		List of the points constituing the contour of the sign.
	shape : int
		Shape of the sign, encoded.

	Returns
	-------
	height : float
		Height of the sign in the image, in pixels.

	"""
	if shape == 2 or shape == 4:
		if number_of_sides < 15:
			height = get_sign_height_circle(img, contour)
		else:
			height = None
	elif shape == 0 or shape == 1 or shape == 9:
		if number_of_sides == 3:
			if shape == 0:
				height = get_sign_height_triangle(img, contour, True)
			else:
				height = get_sign_height_triangle(img, contour, False)
		else:
			height = None
	else:
		if number_of_sides == 4:
			height = get_sign_height_rectangle(img, contour, tag)
		else:
			height = None
	return height

def get_sign_height_circle(img, contour):
	"""
	This function returns the height of a rond sign, considering the different
	shapes or colors it can have.

	Parameters
	----------
	img : ndarray
		Cropped image containing the sign.
	contour : ndarray
		List of the points constituing the contour of the sign.

	Returns
	-------
	height_calculated : float
		Height of the sign, in pixels.

	"""
	liste_pixels = make_liste_contour(contour)

	p1 = min(liste_pixels, key=lambda coord: coord[0])
	p2 = max(liste_pixels, key=lambda coord: coord[0])
	p3 = min(liste_pixels, key=lambda coord: coord[1])
	p4 = max(liste_pixels, key=lambda coord: coord[1])
	
	color1 = get_pixel_rgb(img, p1[0] + 4, p1[1])
	color2 = get_pixel_rgb(img, p2[0] - 4, p2[1])
	color3 = get_pixel_rgb(img, p3[0], p3[1] + 4)
	color4 = get_pixel_rgb(img, p4[0], p4[1] - 4)
	liste_couleurs = (color1, color2, color3, color4)
	verif = []
	for color in liste_couleurs:
		R = color[0]
		G =color[1]
		B = color[2]
		C = int(G) + int(B)
		if R > 0.75*C:
			verif.append(R)
	if len(verif)>=3:
		# Case of the extern contour
		# We calculate the center of the base
		height_calculated = (distance(p1,p2) + distance(p3, p4)) / 2
	else:
		# Case of the intern contour
		# TODO
		height_calculated = None
	return height_calculated

def get_sign_height_rectangle(img, contour, tag):
	"""
	
	This function returns the height of a rectangular sign, considering the different
	shapes or colors it can have.
	
	Parameters
	----------
	img : ndarray
		Cropped image containing the sign.
	contour : ndarray
		List of the points constituing the contour of the sign.
	tag : String
		Code identifying the sign.

	Returns
	-------
	height_calculated : Float
		Height of the sign.

	"""
	list_pixels = make_liste_contour(contour)
	# Peculiar squares and rectangles which could not be treated right
	blue_square_cases = ["CE22", "CE16", "CE14", "CE3a", "CE2e"]
	diamond_cases = ["AB6", "AB7"]
	
	top_left = min(list_pixels, key=lambda p: p[0] + p[1])
	top_right = max(list_pixels, key=lambda p: (p[0], -p[1]))
	bottom_left = min(list_pixels, key=lambda p: (p[0], -p[1]))
	bottom_right = max(list_pixels, key=lambda p: p[0] + p[1])
	
	# Calculation of points in the middle of the top and bottom
	middle_top = (int(((top_left[0] + top_right[0])/2)),
		 int(((top_left[1] + top_right[1])/2)))
	middle_bottom = (int(((bottom_left[0] + bottom_right[0])/2)),
			int(((bottom_left[1] + bottom_right[1])/2)))
	
	# Case disjonction
	if tag in blue_square_cases: # Color : blue
		# Let's take a look at the colors near interest points
		color1 = get_pixel_rgb(img, top_left[0] + 4, top_left[1]+4)
		color2 = get_pixel_rgb(img, top_right[0] - 4, top_right[1]+4)
		color3 = get_pixel_rgb(img, bottom_left[0] + 4, bottom_left[1]-4)
		color4 = get_pixel_rgb(img, bottom_right[0] - 4, bottom_right[1]-4)
		
		list_colors = (color1, color2, color3, color4)
		verif = []
		for color in list_colors: # Tchecking the color
			R = color[0]
			G = color[1]
			B = color[2]
			J = int(R) + int(G)
			if B > 0.75 * J:
				verif.append(B)
		if len(verif)>=3:
			# Case of the extern contour
			# We calculate the height
			height_calculated = (distance(top_left, bottom_left) + distance(top_right, bottom_right)) / 2
			
			cv2.line(img, middle_bottom, middle_top, (255, 0, 255), 1)
		else:
			# Case of the intern contour
			
			print(top_left, top_right, bottom_left, bottom_right)
			cv2.circle(img, top_left, 1, (255, 0, 0), 2) # bleu
			cv2.circle(img, top_right, 1, (0, 255, 0), 2) # vert
			cv2.circle(img, bottom_left, 1, (0, 255, 255), 2) # jaune
			cv2.circle(img, bottom_right, 1, (255, 0, 255), 2) # magenta
			print(middle_bottom, middle_top)
			cv2.circle(img, middle_top, 1, (255, 255, 255), 2) # blanc
			cv2.circle(img, middle_bottom, 1, (0, 0, 0), 2) # noir
			
			# Calculation of the image contour
			imgGray = BGRtoGRAY(img)
			imgEdges = DetectionContours(imgGray)
			
			plotting.show_image(imgEdges, "gray")
			middle_top_prime, middle_bottom_prime = middle_top, middle_bottom
			
			# Calculation of the equation of the line representing the height
			if middle_top[0] != middle_bottom[0]:
				# y = b - ax because the origin is in the top left corner
				a = (middle_top[1] - middle_bottom[1])/(middle_bottom[0] - middle_top[0])
				b = middle_top[1] + a * middle_top[0]
				
				# We check the pixels above middle_top to see which one is on the image contour
				for y in range(middle_top[1] - 5, -1, -1):
					xCalculated = (b - y) / a
					# Is the point on an image contour ?
					if imgEdges[y, int(xCalculated)] == 255:
						middle_top_prime = (int(xCalculated), y)
						break
					# Because we approximate the value of x, we look in the previous pixel too
					elif imgEdges[y, int(xCalculated) - 1] == 255:
						middle_top_prime = (int(xCalculated) - 1, y)
						break
				
				# We do the same for middle_bottom, for the points under middle_bottom
				for y in range(middle_bottom[1] + 5, img.shape[0]):
					xCalculated = (b - y) / a
					# Is the point on an image contour ?
					if imgEdges[y, int(xCalculated)] == 255:
						middle_bottom_prime = (int(xCalculated), y)
						break
					# Because we approximate the value of x, we look in the previous pixel too
					elif imgEdges[y, int(xCalculated) - 1] == 255:
						middle_bottom_prime = (int(xCalculated) - 1, y)
						break
			else:
				# It is a vertical line, represented by : x = c
				c = middle_top[0]
				
				# Check if points above middle_top are on the contour too
				for y in range(middle_top[1] - 2, -1, -1):
					# Is the point on an image contour ?
					if imgEdges[y, c] == 255:
						middle_top_prime = (c, y)
						break
				
				# Same with points under p4
				for y in range(middle_bottom[1] + 2, img.shape[0]):
					# Is the point on an image contour ?
					if imgEdges[y, c] == 255:
						middle_bottom_prime = (c, y)
						break
			
			height_calculated = distance(middle_bottom_prime, middle_top_prime)
			
			cv2.line(img, middle_bottom_prime, middle_top_prime, (255, 0, 255), 1)
			return height_calculated
		
	elif tag in diamond_cases: # Color : yellow
		# In the case of the diamond, we must redefine the points
		top = min(list_pixels, key=lambda coord: coord[1])
		bottom = max(list_pixels, key=lambda coord: coord[1])
		right = max(list_pixels, key=lambda coord: coord[0])
		left = min(list_pixels, key=lambda coord: coord[0])
		color1 = get_pixel_rgb(img, top[0], top[1]+4)
		color2 = get_pixel_rgb(img, bottom[0], bottom[1]-4)
		color3 = get_pixel_rgb(img, left[0] + 4, left[1])
		color4 = get_pixel_rgb(img, right[0] - 4, right[1])
		
		list_colors = (color1, color2, color3, color4)
		verif = []
		for color in list_colors: # Tchecking the color
			R = color[0]
			G = color[1]
			B = color[2]
			J = int(R) + int(G)
			if B < 0.75 * J: # Do we have a yellow color ?
				verif.append(B)
		if len(verif)>=3:
			# Case of the extern contour
			# we calculate the height
			height_calculated = distance(top, bottom)
		else:
			# Case of the intern contour
			# TODO
			return None
	else:
		height_calculated = (distance(top_left, bottom_left) + distance(top_right, bottom_right)) / 2

		cv2.line(img, middle_bottom, middle_top, (255, 0, 255), 1)
	
	return height_calculated

def get_sign_height_triangle(img, contour, boolean):
	"""
	This function checks what part of the sign the contour found and, depending on it,
	throws to sign height calculation.

	Parameters
	----------
	img : ndarray
		Cropped image containing the sign.
	contour : ndarray
		List of the points constituing the contour of the sign.
	boolean : bool
		Signify the orientation of the triangle : to the top or to the left

	Returns
	-------
	height_calculated : float
		Height of the sign, in pixels.

	"""
	list_pixels = make_liste_contour(contour)
	# We get the coords of the vertex of the triangle
	p1 = min(list_pixels, key=lambda coord: coord[0])
	p2 = max(list_pixels, key=lambda coord: coord[0])
	# p3 is the vertex at the top of the image, p4 is at the bottom of it
	if boolean == True:
		p3 = min(list_pixels, key=lambda coord: coord[1])
		color3 = get_pixel_rgb(img, p3[0], p3[1] + 4)
		
		x = math.ceil((p1[0] + p2[0])/2)
		y = math.ceil((p1[1] + p2[1])/2)
		p4 = (x,y)
	else:
		p4 = max(list_pixels, key=lambda coord: coord[1])
		color3 = get_pixel_rgb(img, p4[0], p4[1] - 4)
		
		x = math.ceil((p1[0] + p2[0])/2)
		y = math.ceil((p1[1] + p2[1])/2)
		p3 = (x,y)
	
	# Looking at the internals pixels colors to know if we have
	# a intern or extern contour
	color1 = get_pixel_rgb(img, p1[0] + 4, p1[1]-4)
	color2 = get_pixel_rgb(img, p2[0] - 4, p2[1]-4)
	
	list_colors = (color1, color2, color3)
	verif = []
	# Checking the color
	for color in list_colors:
		R = color[0]
		G = color[1]
		B = color[2]
		C = int(G) + int(B)
		if R > 0.75 * C:
			verif.append(R)
			
	if len(verif)>=2:
		## Case of the extern contour
		height_calculated = distance(p3,p4)
		cv2.line(img, p3, p4, (255, 0, 255), 1)
	else:
		## Case of the intern contour
		# Calculation of the image contour
		imgGray = BGRtoGRAY(img)
		imgEdges = DetectionContours(imgGray)
		
		# Calculation of the equation of the line representing the height
		if p3[0] != p4[0]:
			# y = b - ax because the origin is in the top left corner
			a = (p3[1] - p4[1])/(p4[0] - p3[0])
			b = p3[1] + a * p3[0]
			p3_prime, p4_prime = p3, p4
			
			# We check the pixels above p3 to see which one is on the image contour
			for y in range(p3[1] - 2, -1, -1):
				xCalculated = (b - y) / a
				# Is the point on an image contour ?
				if imgEdges[y, int(xCalculated)] == 255:
					p3_prime = (int(xCalculated), y)
					break
				# Because we approximate the value of x, we look in the previous pixel too
				elif imgEdges[y, int(xCalculated) - 1] == 255:
					p3_prime = (int(xCalculated) - 1, y)
					break
			
			# We do the same for p4, for the points under p4
			for y in range(p4[1] + 2, img.shape[0]):
				xCalculated = (b - y) / a
				# Is the point on an image contour ?
				if imgEdges[y, int(xCalculated)] == 255:
					p4_prime = (int(xCalculated), y)
					break
				# Because we approximate the value of x, we look in the previous pixel too
				elif imgEdges[y, int(xCalculated) - 1] == 255:
					p4_prime = (int(xCalculated) - 1, y)
					break
		else:
			# It is a vertical line, represented by : x = c
			c = p3[0]
			
			# Check if points above p3 are on the contour too
			for y in range(p3[1] - 2, -1, -1):
				# Is the point on an image contour ?
				if imgEdges[y, c] == 255:
					p3_prime = (c, y)
					break
			
			# Same with points under p4
			for y in range(p4[1] + 2, img.shape[0]):
				# Is the point on an image contour ?
				if imgEdges[y, c] == 255:
					p4_prime = (c, y)
					break
		
		# We can then calculate the height
		height_calculated = distance(p3_prime, p4_prime)
		cv2.line(img, p3_prime, p4_prime, (255, 0, 255), 1)
	
	return height_calculated


def distance(point1, point2):
	"""
	
	This function returns the distance between two points
	
	Parameters
	----------
	point1 : tuple
		Point.
	point2 : tuple
		Point.

	Returns
	-------
	TYPE: Float
		Distance between the two points.

	"""
	return np.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def get_pixel_rgb(img, row, col):
	"""
	This function returns the color of a pixel, in RGB

	Parameters
	----------
	img : ndarray
		Cropped sign image.
	row : int
		row identifiant.
	col : int
		Column identifiant.

	Returns
	-------
	real_color : list
		Color in RGB.

	"""
	pixel_rgb = img[col, row]
	R = pixel_rgb[2]
	G = pixel_rgb[1]
	B = pixel_rgb[0]
	
	real_color = [R,G,B]
	return real_color


def is_the_sign_treatable(img, contour, number_of_sides, shape):
	"""
	
	This function returns a boolean : True if the sign is treatable,
	False if it's not.
	
	Parameters
	----------
	img : ndarray
		Cropped image of the sign.
	contour : ndarray
		List of points that draws the biggest polygon in the cropped image.
	number_of_sides : int
		Number of sides of the polygon found, should me the same as the number of sides of the shape.
	shape : int
		Encoded shape of the sign.

	Returns
	-------
	bool
		treatable aspect of the sign : True if it is treatable, False if it's not.

	"""
	if number_of_sides>20:
		return False
	list_points = make_liste_contour(contour)
	sign_area = area_of_point_cloud(list_points)
	height, width, _ = img.shape
	img_area = height * width
	if sign_area < 0.05 * img_area:
		return False
	else:
		return True
	
def area_of_point_cloud(points):
	"""
	
	This functions calculates the convex hull of the points found, that should be the
	contour of the sign, and then returns the area of the convex hull.

	Parameters
	----------
	points : List
		List of the points making the contour of the sygn : these points draw the polygon.

	Returns
	-------
	area : Float
		Area of the convex hull of the points.

	"""
	points_array = np.array(points)
	hull = ConvexHull(points_array)
	indices = hull.vertices
	convex_hull_points = points_array[indices]
	# Area of the convex hull
	area = 0.5 * np.abs(np.dot(convex_hull_points[:, 0], np.roll(convex_hull_points[:, 1], 1)) - 
						np.dot(convex_hull_points[:, 1], np.roll(convex_hull_points[:, 0], 1)))
	return area

if __name__ == '__main__':
	# On importe et on lit le CSV
	dictionnaire_source = "panodico.csv"
	dico = csv_reader(dictionnaire_source)
	
	folder = "./DATA_BASE_SIMULEE"
	
	dirs = os.listdir(folder)
	for category in dirs: # On récupère chaque nom de dossier
		print("CATEGORY ", category)
		if category[:3] == "B14":
			tag = "B14"
		else:
			tag = category
		
		count = 1
		workfolder = os.listdir(folder+ "/" + category) #On construit les chemins d'accès
		for file in workfolder: # On parcourt chaque catégorie de panneau
			# print(folder + "/" + category + "/" + file)
			count += 1
			picture_path = folder+ "/" + category + "/" + file
			#print("PICTURE PATH ", picture_path)
			img = cv2.imread(picture_path) # Reading the image with cv2
			imgGray = BGRtoGRAY(img) # On la transforme en niveaux de gris
			imgEdges = DetectionContours(imgGray) # Finding the contours of the image
			shape = get_shape(tag, dico) # Getting the shape of the sign, according to the dictionnary
			#print("SHAPE ", shape)
			
			approximated_polygon, number_of_sides = get_contour(img, imgEdges, shape)
			center_in_cropped_sign = get_center_in_cropped_sign(img, shape, imgEdges, approximated_polygon, number_of_sides) # Process to get the center of the image
			if center_in_cropped_sign is None:
				continue
			try:
				istreatable = is_the_sign_treatable(img, approximated_polygon, number_of_sides, shape)
			
				if not istreatable:
					print("Ce panneau ne peut pas être traité")
					continue
			except Exception as e:
				print(e)
			w,h,x,y = extraction.get_whxy_from_img_path(picture_path) # Getting the cropped sign informations
			final_center = find_center_in_original_picture(img, center_in_cropped_sign, x, y) # Getting the center of the sign in the original image from panoramax
			#print("FINAL CENTER ", final_center)
			#plotting.show_image(img, title='Objects Detected')
			
			height_sign = get_sign_height(img, approximated_polygon, shape, tag) # Getting the height of the sign
			plotting.show_image(img, title='Objects Detected')
