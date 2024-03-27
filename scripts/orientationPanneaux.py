# Déterminer l'orientation d'un panneau de signalisation à partir d'une photo

import cv2
from matplotlib import pyplot as plt


### 1/ Détection des contours

# Convertir l'image en niveaux de gris
def BGRtoGRAY(img):
	gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	return gray

# Détection des contours par filtre de Canny
def DetectionContours(imgGray):
	imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 0)
	edges = cv2.Canny(imgBlur, 50, 150)
	return edges

# # Détection des contours par filtre de Sobel
# def DetectionContours_2(imgGray):
# 	imgBlur = cv2.GaussianBlur(imgGray, (7, 7), 0)
# 	gradient_x = cv2.Sobel(imgBlur, cv2.CV_64F, 1, 0, ksize=3)
# 	gradient_y = cv2.Sobel(imgBlur, cv2.CV_64F, 0, 1, ksize=3)
# 	edges = cv2.magnitude(gradient_x, gradient_y)
# 	return edges

# # Détection des contours par filtre Laplacian
# def DetectionContours_3(imgGray):
# 	imgBlur = cv2.GaussianBlur(imgGray, (7, 7), 0)
# 	edges = cv2.Laplacian(imgBlur, cv2.CV_64F)
# 	edges = cv2.convertScaleAbs(edges)  # Convertir en valeurs d'entiers 8 bits
# 	return edges

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

def comparaison(listImg):
	for i in range(len(listImg)):
		img = images[i]
		imgGray = BGRtoGRAY(img)
		imgEdges = DetectionContours(imgGray)
		affichagex3(img, imgGray, imgEdges)








if __name__ == '__main__':
	
	path = '/home/formation/Documents/TSIGirardinClaire/Projet/TSI_panoramax/data_test/cropped_signs/'
	listImg = ['A3_tlse_2.png', 'A3_tlse_2bis.png', 'B14_tlse_1.png','B14_tlse_1bis.png', 'B14_tlse_2.png', 'B14_tlse_2bis.png']
	# Charger les images
	images = []
	for nameImg in listImg:
		images.append(cv2.imread(path+nameImg))
	
	comparaison(listImg)
	
	
	
	
	
	
	
	
	
	
	