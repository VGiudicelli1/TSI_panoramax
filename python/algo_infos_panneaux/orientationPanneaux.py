import numpy as np
import cv2
import math as m
import os.path

import contourDetection as cd





# Fonction pour calculer l'angle BAC
def angle3points(A, B, C):

    # Vecteurs AB et BC
    AB = (B[0] - A[0], B[1] - A[1])
    AC = (C[0] - A[0], C[1] - A[1])

    # Produit scalaire de AB et AC
    dot_product = AB[0] * AC[0] + AB[1] * AC[1]

    # Normes de AB et AC
    norm_AB = cd.norme(A, B)
    norm_AC = cd.norme(A, C)
    
    if norm_AB == 0 or norm_AC == 0:
        return "error"

    # Calcul de l'angle en radians
    cosX = dot_product / (norm_AB * norm_AC)
    if -1 <= cosX <= 1:    
        theta_radians = m.acos(cosX)
    else:
        return "error"

    # Conversion de l'angle en degrés
    theta_degrees = m.degrees(theta_radians)

    return theta_degrees


def centrePoint(point1, point2):
    """
    Calcule le point milieu entre deux points donnés.
    
    Args:
        point1 (tuple): Les coordonnées du premier point sous forme de tuple (x1, y1).
        point2 (tuple): Les coordonnées du deuxième point sous forme de tuple (x2, y2).
        
    Returns:
        tuple: Les coordonnées du point milieu sous forme de tuple (x_mid, y_mid).
    """
    x1, y1 = point1
    x2, y2 = point2
    
    x_mid = (x1 + x2) / 2
    y_mid = (y1 + y2) / 2
    
    return (x_mid, y_mid)






def orientationTriangle(coords):
    # coords 0 => point à gauche
    # coords 1 => point à droite
    # coords 2 => point en haut (ou en bas)
    
    beta = angle3points(coords[0], coords[1], coords[2])
    gamma = angle3points(coords[1], coords[0], coords[2])
    
    diff_angles = beta - gamma
    
    
    
    if abs(diff_angles) < 5:  # Si la différence est proche de zéro, le panneau est face à la caméra
        return 0
    elif diff_angles > 0:  # Si la différence est positive, le panneau est tourné vers la droite
        return round(diff_angles, -1)  # Arrondir l'angle avec une précision de 10 degrés
    else:  # Si la différence est négative, le panneau est tourné vers la gauche
        return round(diff_angles, -1)  # Arrondir l'angle avec une précision de 10 degrés

    
    


def orientationRectangle(coords):

    a = cd.norme(coords[1], coords[3])
    b = cd.norme(coords[2], coords[3])
    
    angleOrientation = (1 - b/a) * 90
    
    if round(angleOrientation, -1) == -0.0:
        return 0.0
    
    # orientation à faire
    
    pnt01 = centrePoint(coords[0], coords[1])
    pnt13 = centrePoint(coords[1], coords[3])
    pnt23 = centrePoint(coords[2], coords[3])
    pnt02 = centrePoint(coords[0], coords[2])
    
    alpha = angle3points(pnt02, pnt01, pnt23)
    beta = angle3points(pnt13, pnt01, pnt23)
    
    if beta > alpha: # panneau tourné vers la droite
        return round(angleOrientation, -1)
    else:
        return round(-angleOrientation, -1)
    


def orientationDiamond(coords):

    a = cd.norme(coords[0], coords[2])
    b = cd.norme(coords[1], coords[3])
    
    angleOrientation = (1 - b/a) * 90
    
    if round(angleOrientation, -1) == -0.0:
        return 0.0
    
    alpha = angle3points(coords[3], coords[2], coords[0])
    beta = angle3points(coords[1], coords[0], coords[2])
    
    
    
    if beta > alpha: # panneau tourné vers la droite
        return round(angleOrientation, -1)
    else:
        return round(-angleOrientation, -1)



def orientationCercle(coords):
    # Convertir la liste de tuples en un tableau NumPy
    coords_array = np.array(coords, dtype=np.float32)
    
    # Ajuster une ellipse au contour du cercle
    ellipse = cv2.fitEllipse(coords_array)
    

    # Calculer l'aspect ratio de l'ellipse
    aspect_ratio = ellipse[1][0] / ellipse[1][1]
    
    angleOrientation = (1 - aspect_ratio) * 90 
    
    if round(angleOrientation, -1) == -0.0:
        return 0.0
    
    return round(angleOrientation, -1)
    




def calculOrientation(coords, tagB):
    if tagB == "triangle":
        return orientationTriangle(coords)
    if tagB == "rectangle":
        return orientationRectangle(coords)
    if tagB == "diamond":
        return orientationDiamond(coords)
    if tagB == "cercle":
        return orientationCercle(coords)







if __name__ == '__main__':
    
    # On importe et on lit le CSV
    dictionnaire_source = "../data/panodico.csv"
    dico = cd.csvReader(dictionnaire_source)
    
    folder = "../DATA_BASE_SIMULEE"
    dirs = os.listdir(folder)

    count = 0

    for tag in dirs: # On récupère chaque nom de dossier
    
        if tag == ".DS_Store":
            pass
        
        else:    
            workfolder = os.listdir(folder+ "/" + tag) #On construit les chemins d'accès
            
            for file in workfolder: # On parcourt chaque catégorie de panneau
                if file == ".DS_Store":
                    pass
                else:
                    count += 1
                    picture_path = folder+ "/" + tag + "/" + file
                    img = cv2.imread(picture_path) # Reading the image with cv2
                    imgGray = cd.BGRtoGRAY(img) # On la transforme en niveaux de gris
                    imgEdges = cd.detectionContours(imgGray) # Finding the contours of the image
                    shape = cd.getShape(tag, dico) # Getting the shape of the sign, according to the dictionnary
                    approximated_polygon, number_of_sides = cd.getContour(img, imgEdges, shape)
                    
                    coords, tagB = cd.getCoordsInCroppedSign(img, shape, imgEdges, approximated_polygon, number_of_sides, count, tag)
                    
                    
                    # PAR CALCUL D'ANGLE ET DE DISTANCE
                    if coords is not None:
                        print(count)
                        orientation = calculOrientation(coords, tagB) # CALCUL L'ORIENTATION DU PANNEAU EN DEGREES
                        print("orientation : "+str(orientation))
                        print('\n')
                    



