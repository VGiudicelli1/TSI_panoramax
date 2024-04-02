#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 14:32:17 2024

@author: formation
"""

import cv2
import numpy as np
import math
import plotting


def make_liste_contour(contour):
    liste_pixels =[]
    for pixel in contour:
        x = pixel[0][0]
        y = pixel[0][1]
        coord = (x,y)
        liste_pixels.append(coord)
    return liste_pixels

def find_sign_center_circle(img, max_contour):
    liste_x = []
    liste_y = []
    for point in max_contour:
        point = point[0]
        liste_x.append(point[0])
        liste_y.append(point[1])
    moy_x = math.ceil(np.mean(liste_x))
    moy_y = math.ceil(np.mean(liste_y))
    center = (moy_x,moy_y)
    cv2.circle(img, center, 1, (0, 255, 0), -1)
    plotting.show_image(img, title='Objects Detected')
    return center

def find_sign_center_triangle(img, contour):
    liste_pixels = make_liste_contour(contour)
    # Récupérer la coordonnée avec le x minimum
    coord_x_min = min(liste_pixels, key=lambda coord: coord[0])
    coord_x_max = max(liste_pixels, key=lambda coord: coord[0])
    coord_y_min = min(liste_pixels, key=lambda coord: coord[1])
    
    x = math.ceil((coord_x_min[0] + coord_x_max[0] + coord_y_min[0])/3)
    y = math.ceil((coord_x_min[1] + coord_x_max[1] + coord_y_min[1])/3)
    center = (x,y)

    plotting.show_image_triangle(img, coord_x_min, coord_x_max, coord_y_min, center)
    return center
    
def find_sign_center_rectangle(img, contour):
    liste_pixels = make_liste_contour(contour)
    #On initialise : 
    min_x = float('inf')
    max_x = float('-inf')
    min_y = float('inf')
    max_y = float('-inf')
    for coord in liste_pixels:
        x, y = coord
        min_x = min(min_x, x)
        max_x = max(max_x, x)
        min_y = min(min_y, y)
        max_y = max(max_y, y)

    # Trouver les coins à partir des coordonnées extrêmes
    corners = [(min_x, min_y), (min_x, max_y), (max_x, max_y), (max_x, min_y)]
    x = (corners[0][0] + corners[1][0] + corners[2][0] + corners[3][0]) / 4
    y = (corners[0][1] + corners[1][1] + corners[2][1] + corners[3][1]) / 4
    center = (x,y)

    plotting.show_image_rectangle(img, corners, center)
    
    return center