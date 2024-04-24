import python.trouver_centre_panneau as tcp
import python.plotting as plt
import python.search_api.api as api
import python.search_api.database as db

from matplotlib.pyplot import savefig
import os
import shutil
import time
import cv2

# Relative path that will be used in the test
path_dico = "../data/panodico.csv"
path_pictures = "../../pictures"
path_save_pb_none_signs = "../quality/pb/none"
path_save_pb_no_treatable_signs = "../quality/pb/non-treatable"
path_save_pb_exception_signs = "../quality/pb/exception"
path_save_original_signs = "../quality/original_signs"
path_save_modify_signs = "../quality/modify_signs"


if __name__ == "__main__":
	start = time.time()
	# Create the dictionnary
	dico = tcp.csv_reader(path_dico)
	
	# Create a dictionnary with the number of signs by value in the dico
	dico_values = {}
	
	# 
	pb = ""
	
	# Get the connection
	connection = db.getConnection("127.0.0.1")
	
	total_pictures = 0
	# Browse all kind of signs contains in the dictionnary
	for code in dico:
		# Number of pictures
		count_pictures = 0
		# Select 10 pictures with this code
		cursor = db.selectCroppedSignsByCode(connection, code, limit = 10)
		# Get the names of the columns
		columns = [desc[0] for desc in cursor.description]
		
		# Browse the result
		for row in cursor:
			try:
				count_pictures += 1
				filename = db.getValueAtColumn(row, columns, "filename")
				code = db.getValueAtColumn(row, columns, "code")
				relative_path = db.getPathFromRow(row, columns)
				
				path_cropped_sign = os.path.join(path_pictures, relative_path)
				path_save = os.path.join(path_save_original_signs, "{}-{}".format(code, filename))
				
				img = cv2.imread(path_cropped_sign)
				imgGray = tcp.BGRtoGRAY(img)
				imgEdges = tcp.DetectionContours(imgGray)
				shape = tcp.get_shape(code, dico)
				
				approximated_polygon, number_of_sides = tcp.get_contour(img, imgEdges, shape)
				center_in_cropped_sign = tcp.get_center_in_cropped_sign(img, shape, imgEdges, approximated_polygon, number_of_sides)
				if center_in_cropped_sign is None:
					print(path_cropped_sign)
					print("Le centre est None")
					pb += "{} : Le centre est None.\n".format(path_cropped_sign)
					path_save = os.path.join(path_save_pb_none_signs, "{}-{}".format(code, filename))
					
					shutil.copy2(path_cropped_sign, path_save)
					continue
				try:
					istreatable = tcp.is_the_sign_treatable(img, approximated_polygon, number_of_sides, shape)
				
					if not istreatable:
						print(path_cropped_sign)
						print("Ce panneau ne peut pas être traité")
						path_save = os.path.join(path_save_pb_no_treatable_signs, "{}-{}".format(code, filename))
						
						pb += "{} : Ce panneau ne peut être traité.\n".format(path_cropped_sign)
						shutil.copy2(path_cropped_sign, path_save)
				
						continue
				except Exception as e:
					print(path_cropped_sign)
					print(e)
					path_save = os.path.join(path_save_pb_exception_signs, "{}-{}".format(code, filename))
					
					shutil.copy2(path_cropped_sign, path_save)
					pb += "{} : Le problème suivant est arrivé : \n{}\n".format(path_cropped_sign, e)
			
				
				cv2.circle(img, center_in_cropped_sign, 1, (0, 255, 0), 4)
				height_sign = tcp.get_sign_height(img, approximated_polygon, shape, number_of_sides, code)
				#plt.show_image(img, title='Center and height')
				shutil.copy2(path_cropped_sign, path_save)
				
				path_save_modify = os.path.join(path_save_modify_signs, "Modify {}-{}".format(code, filename))
	
				plt.save_image(img, path_save_modify, title = "Center and height")
			except Exception as e:
				print(path_cropped_sign)
				print(e)
				path_save = os.path.join(path_save_pb_exception_signs, "{}-{}".format(code, filename))
				
				shutil.copy2(path_cropped_sign, path_save)
				pb += "{} : Le problème suivant est arrivé : \n{}\n".format(path_cropped_sign, e)
				
		if dico[code] in dico_values:
			dico_values[dico[code]] += count_pictures
		else:
			dico_values[dico[code]] = count_pictures
		total_pictures += count_pictures
			
	end = time.time()
	print("The update took {} seconds".format(end - start))
	print("Number of pictures : {}".format(total_pictures))
	print(db.itemAlreadyInDatabase(connection, 1, "cropped_sign"))
	
	with open("../pb.txt", 'w') as f:
		f.writelines(pb)