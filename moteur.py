#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 09:37:54 2024

@author: Victorien Ollivier
"""

import cv2
from matplotlib import pyplot as plt
import os
from os import listdir
import numpy as np
import math
import plotting
import find_center_shape
import extraction

# Convertir l'image en niveaux de gris
def BGRtoGRAY(img):
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	return gray

# Détection des contours par filtre de Canny
def DetectionContours(imgGray):
	imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 0)
	edges = cv2.Canny(imgBlur, 50, 150)
	return edges


def find_sign(image, edges):
    # On trouve les contours dans l'image
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    # Approximer le contour avec un polygone
    largest_contour = contours[0]
    epsilon = 0.02 * cv2.arcLength(largest_contour, True)
    approx = cv2.approxPolyDP(largest_contour, epsilon, True)
    
    # Déterminer le nombre de côtés du polygone
    sides = len(approx)
    
    # Identifier la forme
    shape = ""
    if sides == 3:
        shape = "triangle"
    elif sides == 4:
        x, y, w, h = cv2.boundingRect(approx)
        aspect_ratio = float(w) / h
        shape = "square" if 0.90 <= aspect_ratio <= 1.10 else "rectangle"
    elif sides > 4:
        shape = "cercle"
    else:
        shape = "autre"
    
    # Dessiner le contour et le polygone approximatif sur l'image originale
    cv2.drawContours(image, [largest_contour], -1, (0, 255, 0), 2)
    cv2.drawContours(image, [approx], -1, (255, 0, 0), 2)
    
    # Afficher l'image
    #plotting.show_image(image, title='Objects Detected')
    
    return shape, largest_contour

def find_center_func(img, sign):
    shape = sign[0]
    contour = sign[1]
    if shape =="cercle":
        center_point = find_center_shape.find_sign_center_circle(img, contour)
    elif shape == "triangle":
        center_point = find_center_shape.find_sign_center_triangle(img, contour)
    elif shape =="square":
        center_point = center_point = find_center_shape.find_sign_center_rectangle(img, contour)
    elif shape=="rectangle":
        center_point = find_center_shape.find_sign_center_rectangle(img, contour)
    else:
        center_point = False
    return center_point

def find_center_in_original_picture(img, center, x, y):
    final_x = x + center[0]
    final_y = y + center[1]
    final_center = (final_x,final_y)
    return final_center

if __name__ == '__main__':
    
    folderdir = "/home/formation/Victorien/Projet_Panneau/center_test"
    # im_rond = 'panotest3.jpg'
    # im_carre = 'square2.jpg'
    # im_triangle = 'triangle.jpg'
    # path = im_carre
    for images in os.listdir(folderdir):
        
        path = folderdir+'/'+images
        w,h,x,y = extraction.get_whxy_from_img_path(path)
        #print(path)
        img = cv2.imread(path)
        imgGray = BGRtoGRAY(img)
        imgEdges = DetectionContours(imgGray)
        #plotting.affichagex3(img, imgGray, imgEdges)
        sign = find_sign(img,imgEdges)
        center = find_center_func(img,sign)
        final_center = find_center_in_original_picture(img, center, x, y)
        print("le centre du panneau est : ", final_center)