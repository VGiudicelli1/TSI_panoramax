# Déterminer l'orientation d'un panneau de signalisation à partir d'une photo

import cv2
from matplotlib import pyplot as plt
import numpy as np
import math as m




# Convertir l'image en niveaux de gris
def BGRtoGRAY(img):
      # Vérifier si l'image est vide
      if img is None:
            print("Erreur: Impossible de charger l'image.")
            return None
      
      # Convertir en niveaux de gris
      imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
      return imgGray




# Détection des contours par filtre de Canny (+ ajout d'un filtre Gaussien)
def detectionContours(imgGray):
      imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 0)
      imgEdges = cv2.Canny(imgBlur, 50, 150)
      return imgEdges



def csvReader(path):
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



def norme(p1, p2):
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
      return m.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)



def getShape(tag, dico):
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



# Fonction de formatage
def listContour(contour):
      """
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

      """
      list_pixels =[]
      for pixel in contour:
            x = pixel[0][0]
            y = pixel[0][1]
            coord = (x,y)
            list_pixels.append(coord)
      return list_pixels




def getContour(img, imgEdges, shape):
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
      elif shape == 3: # Losange
            value_for_epsilon = 0.05
      else:
            value_for_epsilon = 0.15
      # Finding contours in the image
      contours, _ = cv2.findContours(imgEdges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

      # Sorting them to get the biggest one
      contours = sorted(contours, key=cv2.contourArea, reverse=True)
      largest_contour = contours[0]
      
      # Approximation of a polygon
      epsilon = value_for_epsilon * cv2.arcLength(largest_contour, True) # Definition of the factor 
      approx = cv2.approxPolyDP(largest_contour, epsilon, True) # Approximation
      sides = len(approx) # Number of sides of the polygon, to know if we found the good form
      return approx, sides



def getCoordsInCroppedSign(img, shape, imgEdges, contour_sign, number_of_sides, count, tag):
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
            Number of sides detected of the polygon

      Returns
      -------
      coords : tuple
            coords of the contours in the cropped image
      tagB : String
            tag of the sign
      """
      if shape == 0: ## Triangle-top case
            if number_of_sides != 3: # If the number of sides is not corresponding to the hoped shape ...
                  coords, tagB = None, None
            else:
                  coords, tagB = getCoordsTriangle(img, contour_sign, True, count) # Or we search the center of the sign (to the top)
                  
      elif shape == 1 or shape == 9: ## Triangle-bottom case
            if number_of_sides != 3: # If the number of sides is not corresponding to the hoped shape ...
                  coords, tagB = None, None
            else:
                  coords, tagB = getCoordsTriangle(img, contour_sign, False, count) # Or we search the center of the sign (to the bottom)
      
      elif shape == 2 :## Octogon case
            if number_of_sides != 8: # If the number of sides is not corresponding to the hoped shape ...
                  coords, tagB = None, None
            else:
                  coords, tagB = getCoordsCircle(img, contour_sign, count) #  Or we search the cneter of the sign (Octogon)
      elif shape == 3 or shape== 5 or shape == 6 or shape == 7 or shape == 8:## Rectangle case
            if number_of_sides != 4: # If the number of sides is not corresponding to the hoped shape ...
                  coords, tagB = None, None
            else:
                  coords, tagB = getCoordsRectangle(img, contour_sign, count, tag) # Or we search the center of the sign (to the bottom)
      else: ## Circle or unrecognized shape case
            coords, tagB = getCoordsCircle(img, contour_sign, count)
      return coords, tagB



def getCoordsTriangle(img, contour_sign, boolean, count):
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
      list_pixels = listContour(contour_sign) # Formatting function
      
      # We get the coords of the vertex of the triangle
      coord_x_min = min(list_pixels, key=lambda coord: coord[0])
      coord_x_max = max(list_pixels, key=lambda coord: coord[0])
      # The third vertex depends on the orientation of the sign
      if boolean == True:
            coord_y = min(list_pixels, key=lambda coord: coord[1])
      elif boolean == False:
            coord_y = max(list_pixels, key=lambda coord: coord[1])

      coords = [coord_x_min, coord_x_max, coord_y]
      showImg(img, coords, title="Img Triangle "+str(count))
      
      tagB="triangle"
      
      return coords, tagB


def getCoordsCircle(img, contour, count):
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
      coords = []
      for point in contour:
            point = point[0]
            coords.append((point[0], point[1]))
      showImg(img, coords, title="Img Cercle "+str(count))
      
      tagB="cercle"
      
      return coords, tagB



def getCoordsRectangle(img, contour, count, tag):
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
      list_pixels = listContour(contour)
      
      # Vérifier la cohérence des coordonnées pour s'assurer qu'elles forment un rectangle
      if len(set(list_pixels)) != 4:
          return None, None
      
      # separate squares from diamonds
      diamonds = ["AB6", "AB7"]
      if tag in diamonds:

          tagB = "diamond"
          
          # We get the coords of the vertex of the triangle
          coord_x_min = min(list_pixels, key=lambda coord: coord[0])
          coord_x_max = max(list_pixels, key=lambda coord: coord[0])
          coord_y_min = min(list_pixels, key=lambda coord: coord[1])
          coord_y_max = max(list_pixels, key=lambda coord: coord[1])

          coords = [coord_y_min, coord_x_max, coord_y_max, coord_x_min]
          
          showImg(img, coords, title="Img Rectangle "+str(count))
      
        
      else:
          tagB="rectangle"
          
          # Sélectionner les 2 points avec les coordonnées y les plus petites
          top_two_y_coords = sorted(list_pixels, key=lambda coord: coord[1])[:2]
          
          # Tri des premiers deux points selon les coordonnées x
          top_two_y_coords_sorted_by_x = sorted(top_two_y_coords, key=lambda coord: coord[0])
          
          # Sélectionner les 2 points avec les coordonnées y les plus grandes
          bottom_two_y_coords = sorted(list_pixels, key=lambda coord: coord[1], reverse=True)[:2]
          
          # Tri des derniers deux points selon les coordonnées x
          bottom_two_y_coords_sorted_by_x = sorted(bottom_two_y_coords, key=lambda coord: coord[0])
          
          # Liste finale triée
          coords = top_two_y_coords_sorted_by_x + bottom_two_y_coords_sorted_by_x
          
          showImg(img, coords, title="Img Rectangle "+str(count))
          
          
      
      return coords, tagB



def showImg(img, coords, title):
        
    plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    
    nbr = len(coords)
      
    for k in range(nbr):
        plt.scatter(*coords[k], color='green')
    
    # plt.scatter(*coords[0], color='red')
    # plt.scatter(*coords[1], color='green')
    # plt.scatter(*coords[2], color='blue')
    # plt.scatter(*coords[3], color='black')

    plt.title(title)
    plt.axis('off')
    plt.show()






