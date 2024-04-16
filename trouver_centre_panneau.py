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
    cv2.drawContours(img, [largest_contour], -1, (0, 255, 0), 2)
    cv2.drawContours(img, [approx], -1, (255, 0, 0), 2)
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
            center_sign = None# ... We just take the center of the cropped sign
        else:
            center_sign = get_center_triangle(img, contour_sign, True) # Or we search the center of the sign (to the top)
            
    elif shape == 1 or shape == 9: ## Triangle-bottom case
        if number_of_sides != 3: # If the number of sides is not corresponding to the hoped shape ...
            center_sign = None# ...  We just take the center of the cropped sign
        else:
            center_sign = get_center_triangle(img, contour_sign, False) # Or we search the center of the sign (to the bottom)
    
    elif shape == 2 :## Octogon case
        if number_of_sides != 8: # If the number of sides is not corresponding to the hoped shape ...
            center_sign = None# ... We just take the center of the cropped sign
        else:
            center_sign = get_center_circle(img, contour_sign) #  Or we search the cneter of the sign (Octogon)
    elif shape == 3 or shape== 5 or shape == 6 or shape == 7 or shape == 8:## Rectangle case
        if number_of_sides != 4: # If the number of sides is not corresponding to the hoped shape ...
            center_sign = None# ... We just take the center of the cropped sign
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


def get_sign_height(img, contour, shape):
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
        if number_of_sides < 8:
            height = get_sign_height_circle(img, contour)
        else:
            height = None
    elif shape == 0 or shape == 1 or shape == 9:
        if number_of_sides == 3:
            height = get_sign_height_triangle(img, contour)
        else:
            height = None
    else:
        if number_of_sides == 4:
            height = get_sign_height_rectangle(img, contour)
        else:
            height = None
    return height

def get_sign_height_circle(img, contour):
    # Calcul des coordonnées pour les pixels décalés
    liste_pixels = make_liste_contour(contour)

    x_min = min(liste_pixels, key=lambda coord: coord[0])
    x_max = max(liste_pixels, key=lambda coord: coord[0])
    y_min = min(liste_pixels, key=lambda coord: coord[1])
    y_max = max(liste_pixels, key=lambda coord: coord[1])
    #print("exemple de coordonnées : ", x_min)
    
    color1 = get_pixel_rgb(img, x_min[0] + 3, x_min[1])
    color2 = get_pixel_rgb(img, x_max[0] - 3, x_max[1])
    color3 = get_pixel_rgb(img, y_min[0], y_min[1] + 3)
    color4 = get_pixel_rgb(img, y_max[0], y_max[1] - 3)
    liste_couleurs = (color1, color2, color3, color4)
    verif = []
    for color in liste_couleurs:
        R = color[0]
        v=color[1]
        v2 = color[2]
        C = int(v) + int(v2)
        #C = color[1] + color[2]
        #print("color R", R)
        #print("value C", C)
        if R > C:
            verif.append(R)
    print("Les couleurs sont :", color1, color2, color3, color4)
    # if len(verif)>= 3:
    #     h1 = np.sqrt((x_min[0] - x_max[0])**2 + (x_min[1] - x_max[1])**2)
    #     h2 = np.sqrt((y_min[0] - y_max[0])**2 + (y_min[1] - y_max[1])**2)
    #     h = (h1 + h2) / 2
        # return h
    # else:
    #     get_hauteur_sign(img,x_min, x_max, y_min, y_max)
    return x_min, x_max, y_min, y_max
    ### TODO ###
    return None

def get_sign_height_triangle(img, contour):
    ### TODO ###
    return None

def get_sign_height_rectangle(img, contour):
    ### TODO ###
    return None


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
    pixel_rgb = img[col, row]  # Assurez-vous d'utiliser les coordonnées dans l'ordre (colonne, ligne)
    R = pixel_rgb[2]
    G = pixel_rgb[1]
    B = pixel_rgb[0]
    
    real_color = [R,G,B]
    return real_color

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
            print("IMAGE ", count)
            picture_path = folder+ "/" + category + "/" + file
            #print("PICTURE PATH ", picture_path)
            img = cv2.imread(picture_path) # Reading the image with cv2
            imgGray = BGRtoGRAY(img) # On la transforme en niveaux de gris
            imgEdges = DetectionContours(imgGray) # Finding the contours of the image
            shape = get_shape(tag, dico) # Getting the shape of the sign, according to the dictionnary
            print("SHAPE ", shape)
            
            approximated_polygon, number_of_sides = get_contour(img, imgEdges, shape)
            center = get_center_in_cropped_sign(img, shape, imgEdges, approximated_polygon, number_of_sides) # Process to get the center of the image
            w,h,x,y = extraction.get_whxy_from_img_path(picture_path) # Getting the cropped sign informations
            final_center = find_center_in_original_picture(img, center, x, y)
            print("FINAL CENTER ", final_center)
            plotting.show_image(img, title='Objects Detected')
            height_sign = get_sign_height(img, approximated_polygon, shape)
            count += 1