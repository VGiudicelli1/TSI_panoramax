import os
import time
import cv2

import python.algo_info_panneaux.trouver_centre_panneau as tcp
import python.algo_info_panneaux.plotting as plt
import python.search_api.api as api
import python.search_api.database as db


if __name__ == "__main__":
	
	# Time of the algorithm
	start = time.time()
	
	# Add a log to save the result in a log file
	log = ""
	logPath = "/home/formation/Documents/TSI/Panoramax/log"
	
	# Dictionnary for the signs
	path_dico = "../data/panodico.csv"
	dico = tcp.csv_reader(path_dico)
	
	# Path of all the cropped sign
	croppedSignPath = "/home/formation/Documents/TSI/Panoramax/pictures"
	
	# Get the connection - "172.31.58.179", password = "tsi23lesboss",
	connection = db.getConnection("172.31.58.179", password = "tsi23lesboss",
							   database="panoramax")
	
	# Select all lines and get the column names
	cursor = db.selectAll(connection, "cropped_sign")
	columns = [desc[0] for desc in cursor.description]
	
	# Browse all lines of the database
	for index, row in enumerate(cursor.fetchall()):
		# Get the path of the relative path of the cropped sign
		rowPath = db.getPathFromRow(row, columns)
		path = os.path.join(croppedSignPath, rowPath)
		
		# Get sign code
		code = db.getValueAtColumn(row, columns, "code")
		
		# Initialise x, y and dz to null values
		x, y, dz = "null", "null", "null"

		# Open the image and transform it to detect the contour
		img = cv2.imread(path)
		imgGray = tcp.BGRtoGRAY(img)
		imgEdges = tcp.DetectionContours(imgGray)
		if code in dico:
			shape = tcp.get_shape(code, dico)
		else:
			print(code)
			continue
		
		try:
			# Check if the image is treatable
			approximated_polygon, number_of_sides = tcp.get_contour(img, imgEdges, shape)
			istreatable = tcp.is_the_sign_treatable(img, approximated_polygon, number_of_sides, shape)
			
			# Calculate the center of the cropped sign
			center_in_cropped_sign = tcp.get_center_in_cropped_sign(img, shape, imgEdges, approximated_polygon, number_of_sides)
			
			# If the center is not found, we take the center of the picture
			# And 60% of the height of the image for dz
			# Same if the image is not treatable
			if center_in_cropped_sign is None or not istreatable:
				(x, y) = tcp.get_image_center(img)
				height, width, _ = img.shape
				
				dz = int(height * 0.6)
			else:
				(x, y) = center_in_cropped_sign
				
				# Calculate the height of the cropped sign
				dz = tcp.get_sign_height(img, approximated_polygon, shape, number_of_sides, code)
				
				if dz is None:
					height, width, _ = img.shape
					
					dz = int(height * 0.6)
		
		except Exception as e:
			print(e)
			# If an exception occurs during the calculation, we do the same that
			# When the center is not detected
			(x, y) = tcp.get_image_center(img)
			height, width, _ = img.shape
			
			dz = int(height * 0.6)
		
		finally:
			
			# Update the cropped sign attributes in the database
			croppedSignId = db.getValueAtColumn(row, columns, "id")
			linesUpdated = db.updateCenterOfSign(connection, croppedSignId, x, y, dz)
			
			if linesUpdated == 0:
				log += "No lines where updated for the cropped sign {}\n".format(rowPath)
			else:
				log += "Values for the cropped sign {} has been updated\n".format(rowPath)
	
	# Save the log into a log file
	with open(os.path.join(logPath, "log.txt"), 'w') as f:
		f.writelines(log)
	
	end = time.time()
	print("The update took {} seconds".format(end - start))