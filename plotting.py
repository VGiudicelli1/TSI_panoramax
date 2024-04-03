#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 14:08:45 2024

@author: formation
"""
import cv2
from matplotlib import pyplot as plt
import numpy as np
import math


def affichagex3(img, imgGray, imgEdges):
	# Afficher l'image originale, de l'image en niveau de gris
	# et de l'image avec détection des contours
	plt.subplot(1, 3, 1), plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
	plt.title('Image originale'), plt.xticks([]), plt.yticks([])
	plt.subplot(1, 3, 2), plt.imshow(imgGray, cmap='gray')
	plt.title('Image niv gray'), plt.xticks([]), plt.yticks([])
	plt.subplot(1, 3, 3), plt.imshow(imgEdges, cmap='gray')
	plt.title('Contours détectés'), plt.xticks([]), plt.yticks([])
	plt.show()
    
    
def show_image(img, title="Image"):
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    plt.title(title)
    plt.axis('off')
    plt.show()
    
    
def show_image_triangle(img, coord1, coord2, coord3, center, title="Image"):
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    
    # Tracer les coordonnées sur l'image
    plt.scatter(*coord1, color='red', label='Coord1')
    plt.scatter(*coord2, color='green', label='Coord2')
    plt.scatter(*coord3, color='blue', label='Coord3')
    plt.scatter(*center, color='blue', label='Center')

    # Ajouter les étiquettes
    plt.text(coord1[0], coord1[1], 'Coord1', fontsize=9, ha='right')
    plt.text(coord2[0], coord2[1], 'Coord2', fontsize=9, ha='right')
    plt.text(coord3[0], coord3[1], 'Coord3', fontsize=9, ha='right')

    plt.title(title)
    plt.axis('off')
    plt.legend()
    plt.show()

def show_image_rectangle(img, corners, center, title="Image"):
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    
    # Tracer les coordonnées sur l'image
    plt.scatter(*corners[0], color='red', label='Coord1')
    plt.scatter(*corners[1], color='green', label='Coord2')
    plt.scatter(*corners[2], color='blue', label='Coord3')
    plt.scatter(*corners[3], color='purple', label='Coord4')
    plt.scatter(*center, color='blue', label='Center')


    plt.title(title)
    plt.axis('off')
    plt.legend()
    plt.show()