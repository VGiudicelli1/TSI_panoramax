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

#### I - Récupération d'informations et de photos, application des filtres #######


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

# Convertir l'image en niveaux de gris
def BGRtoGRAY(img):
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	return gray

# Détection des contours par filtre de Canny
def DetectionContours(imgGray):
	imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 0)
	edges = cv2.Canny(imgBlur, 50, 150)
	return edges


def find_center_in_original_picture(img, center, x, y):
    final_x = x + center[0]
    final_y = y + center[1]
    final_center = (final_x,final_y)
    return final_center

def get_image_center(img):
    height, width = img.shape[:2]
    #print('height', height)
    #print('width', width)
    center_x = width // 2
    center_y = height // 2
    #print('height', center_x)
    #print('width', center_y)
    # Récupérer la valeur du pixel au centre
    center = (center_x, center_y)
    return center

########## II - Récupération de la forme, du contour, et du centre dans le crop ######



# Récupération de la forme recherchée
def get_shape(tag, dico):
    return dico[tag]

# Fonction de répartition de la recherche du contour de panneau en focntion du signe
def get_center_in_cropped_sign(img, shape, imgEdges):
    contour_sign = get_contour(img, imgEdges, shape)
    if shape == 0: ## Cas du triangle : on lance les fonctions
        if contour_sign[1] != 3: # SI le triangle n'a pas été reconnu ...
            center_sign = get_image_center(img)# ... On lance la fonction qui prend le milieu de l'image
        else:
            center_sign = get_center_code_01(img, contour_sign[0], True) # Sinon on cherche le milieu du triangle à l'endroit.
            
    elif shape == 1 or shape == 9: ## Cas du triangle à l'envers : on appelle les fonctions
        if contour_sign[1] != 3: # SI le triangle n'a pas été reconnu ...
            center_sign = get_image_center(img)# ... On lance la fonction qui prend le milieu de l'image
        else:
            center_sign = get_center_code_01(img, contour_sign[0], False) # Sinon on cherche le milieu du triangle à l'envers
    
    elif shape == 2 :## Cas de l'octogone
        if contour_sign[1] != 8: # SI l'octogone n'a pas été reconnu ...
            print("forme du panneau non reconnue")
            center_sign = get_image_center(img)# ... On lance la fonction qui prend le milieu de l'image
        else:
            print("octogone reconnu")
            center_sign = get_center_code_2(img, contour_sign[0]) # Sinon on cherche le milieu du triangle à l'endroit.
    elif shape == 3 or shape== 5 or shape == 6 or shape == 7 or shape == 8:## Cas du rectangle
        if contour_sign[1] != 4: # SI l'octogone n'a pas été reconnu ...
            print("forme du panneau non reconnue")
            center_sign = get_image_center(img)# ... On lance la fonction qui prend le milieu de l'image
        else:
            center_sign = get_center_code_3(img, contour_sign[0]) # Sinon on cherche le milieu du triangle à l'endroit.
    else:
        center_sign = get_center_code_2(img, contour_sign[0])
    return center_sign


# Fonction de formatage
def make_liste_contour(contour):
    liste_pixels =[]
    for pixel in contour:
        x = pixel[0][0]
        y = pixel[0][1]
        coord = (x,y)
        liste_pixels.append(coord)
    return liste_pixels


###### Cas des triangles (cas base en haut, et cas base en bas) ######### 

def get_contour(img, edges, shape):
    
    if shape == 2 or shape == 4:
        value_for_epsilon = 0.02
    elif shape == 0 or shape ==1 or shape == 9 :
        value_for_epsilon = 0.15
    else:
        value_for_epsilon = 0.15
    # On trouve les contours dans l'image
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    
    # Approximer le contour avec un polygone
    largest_contour = contours[0]
    epsilon = value_for_epsilon * cv2.arcLength(largest_contour, True)
    approx = cv2.approxPolyDP(largest_contour, epsilon, True)
    # Déterminer le nombre de côtés du polygone
    sides = len(approx)
    # cv2.drawContours(img, [largest_contour], -1, (0, 255, 0), 2)
    # cv2.drawContours(img, [approx], -1, (255, 0, 0), 2)
    #print("valeur de sides : ", sides)
    which_circle(img, largest_contour)
    cv2.drawContours(img, [largest_contour], -1, (0, 255, 0), 2)
    cv2.drawContours(img, [approx], -1, (255, 0, 0), 2)
    return approx, sides

def get_center_code_01(img, contour_sign, boolean):
    liste_pixels = make_liste_contour(contour_sign)
    # Récupérer la coordonnée avec le x minimum
    coord_x_min = min(liste_pixels, key=lambda coord: coord[0])
    coord_x_max = max(liste_pixels, key=lambda coord: coord[0])
    if boolean == True:
        coord_y_min = min(liste_pixels, key=lambda coord: coord[1])
    elif boolean == False:
        coord_y_min = max(liste_pixels, key=lambda coord: coord[1])
    
    x = math.ceil((coord_x_min[0] + coord_x_max[0] + coord_y_min[0])/3)
    y = math.ceil((coord_x_min[1] + coord_x_max[1] + coord_y_min[1])/3)
    center = (x,y)

    plotting.show_image_triangle(img, coord_x_min, coord_x_max, coord_y_min, center)
    return center

#### Cas de l'octogone ####

def get_center_code_2(img, contour):
    liste_x = []
    liste_y = []
    for point in contour:
        point = point[0]
        liste_x.append(point[0])
        liste_y.append(point[1])
    moy_x = math.ceil(np.mean(liste_x))
    moy_y = math.ceil(np.mean(liste_y))
    center = (moy_x,moy_y)
    cv2.circle(img, center, 1, (0, 255, 0), -1)
    plotting.show_image(img, title='Objects Detected')
    return center

def get_center_code_3(img, contour):
    liste_pixels = make_liste_contour(contour)
    # Récupérer la coordonnée avec le x minimum
    coord_x_min = min(liste_pixels, key=lambda coord: coord[0])
    coord_x_max = max(liste_pixels, key=lambda coord: coord[0])
    coord_y_min = min(liste_pixels, key=lambda coord: coord[1])
    coord_y_max = max(liste_pixels, key=lambda coord: coord[1])
    
    x = math.ceil((coord_x_min[0] + coord_x_max[0] + coord_y_min[0] + coord_y_max[0])/4)
    y = math.ceil((coord_x_min[1] + coord_x_max[1] + coord_y_min[1] + coord_y_max[1])/4)
    center = (x,y)
    corners = []
    corners.append(coord_x_min)
    corners.append(coord_x_max)
    corners.append(coord_y_min)
    corners.append(coord_y_max)
    plotting.show_image_rectangle(img, corners, center)
    return center
    
def which_circle(img, contour):
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
    if len(verif)>= 3:
        h1 = np.sqrt((x_min[0] - x_max[0])**2 + (x_min[1] - x_max[1])**2)
        h2 = np.sqrt((y_min[0] - y_max[0])**2 + (y_min[1] - y_max[1])**2)
        h = (h1 + h2) / 2
        return h
    else:
        get_hauteur_sign(img,x_min, x_max, y_min, y_max)

def get_hauteur_sign(img, p1, p2, p3, p4):
    gray = BGRtoGRAY(img)
    IMGcanny = DetectionContours(gray)  # Utiliser Canny pour détecter les contours

    # Calculer les coefficients des droites P1-P2 et P3-P4 (y = mx + c)
    m1 = (p2[1] - p1[1]) / (p2[0] - p1[0])
    c1 = p1[1] - m1 * p1[0]

    m2 = (p4[1] - p3[1]) / (p4[0] - p3[0])
    c2 = p3[1] - m2 * p3[0]

    matrice_contours = np.zeros_like(IMGcanny)
    # Remplacer les pixels de contour par 1
    matrice_contours[IMGcanny > 0] = 1

    # Parcourir chaque pixel de l'image
    for y in range(img.shape[0]):
        # Vérifier si le pixel valide l'une des deux équations de droite
        
        if (y - m1 * x - c1) * (y - m2 * x - c2) <= 0:
            matrice_contours[y, x] = 2

    # Enregistrer la matrice de contours dans un fichier texte
    np.savetxt("matrice_contours.txt", matrice_contours, fmt='%d')


def get_pixel_rgb(image, row, col):
    pixel_rgb = image[col, row]  # Assurez-vous d'utiliser les coordonnées dans l'ordre (colonne, ligne)
    R = pixel_rgb[2]
    V = pixel_rgb[1]
    B = pixel_rgb[0]
    
    real_color = [R,V,B]
    return real_color

if __name__ == '__main__':
    
    #folder = "C:/Users/Myriam/Documents/IT3/Panoramax/TSI_panoramax/data_test"
    dictionnaire_source = "panodico.csv"
    dico = csv_reader(dictionnaire_source)
    
    folder = "./center_test"
    dirs = os.listdir(folder)
    
    # This would print all the files and directories
    tag = "B14"
    count = 1
    for file in dirs:
        print("IMAGE ", count)
        picture_path = "center_test/" + file
       # print(picture_path)
        img = cv2.imread(picture_path)
        imgGray = BGRtoGRAY(img)
        imgEdges = DetectionContours(imgGray)
        shape = get_shape(tag, dico)
        #print("shape = ", shape)
        center_in_cropped = get_center_in_cropped_sign(img, shape, imgEdges)
        #print("La valeur du centre : ", center_in_cropped)
        w,h,x,y = extraction.get_whxy_from_img_path(picture_path)
        final_center = find_center_in_original_picture(img, center_in_cropped, x, y)
        #print(final_center)
        count +=1
        
    # folder = "/home/formation/Victorien/Projet_Panneau/detectcenter/trié2"
    # source = "/home/formation/Victorien/TSI_panoramax/panneaux_data_limit_100.csv"
    # data = pd.read_csv(source)
    # # Créer une liste pour chaque ligne
    # listes_lignes = data.values.tolist()
    # dictionnaire_source = "/home/formation/Victorien/Projet_Panneau/Code_trouver_centre_panneau/panodico.csv"
    # dico = csv_reader(dictionnaire_source)
    # for element in listes_lignes:
    #     tag = element[3]
    #     if not math.isnan(element[4]):
    #         picture_path = folder + "/"+tag + "-" + element[4] +"/" + element[2]
    #     else:
    #         picture_path = folder + "/"+tag+"/" + element[2]

    #     img = cv2.imread(picture_path)
    #     imgGray = BGRtoGRAY(img)
    #     imgEdges = DetectionContours(imgGray)
    #     shape = get_shape(tag, dico)
    #     center_in_cropped = get_center_in_cropped_sign(img, shape, imgEdges)
    #     print("La valeur du centre : ", center_in_cropped)
    #     w,h,x,y = extraction.get_whxy_from_img_path(picture_path)
    #     final_center = find_center_in_original_picture(img, center_in_cropped, x, y)
    #     print(final_center)
    # Pour l'instant, nous allons travailler sur une seule photo, d'un triangle de type 0
    #photo_path = "/home/formation/Victorien/Projet_Panneau/Code_trouver_centre_panneau/panotest2.jpg"
    #tag = "B14"
    # img = cv2.imread(photo_path)
    # imgGray = BGRtoGRAY(img)
    # imgEdges = DetectionContours(imgGray)
    # shape = get_shape(tag, dico)
    # center_in_cropped = get_center_in_cropped_sign(img, shape, imgEdges)
    # print("La valeur du centre : ", center_in_cropped)
    # w,h,x,y = extraction.get_whxy_from_img_path(photo_path)
    # final_center = find_center_in_original_picture(img, center_in_cropped, x, y)
    # print(final_center)
        