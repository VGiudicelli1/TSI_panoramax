import api
import database as db
import time
import os
import shutil

if __name__ == "__main__":
	
	# Time of the algorithm
	start = time.time()
	
	# Add a log to save the result in a log file
	log = ""
	logPath = "/home/formation/Documents/TSI/Panoramax/log"
	
	# Path of all the cropped sign
	savePicturePath = "/home/formation/Documents/TSI/Panoramax/treatment"
	
	# Get the connection - "172.31.58.179, password = "tsi23lesboss",
	connection = db.getConnection("127.0.0.1", 
							   database="panoramax")
	
	# Select all lines and get the column names
	cursor = db.selectAll(connection, "cropped_sign", limit = 1000)
	columns = [desc[0] for desc in cursor.description]
	
	# If the directory is not created, we create it
	if not os.path.exists(savePicturePath):
		os.makedirs(savePicturePath)
		print("Directory {} created".format(savePicturePath))
	else:
		print("Directory {} already exists".format(savePicturePath))
		
	## Browse all lines of the database
	for index, row in enumerate(cursor.fetchall()):
		# Get the path of the relative path of the cropped sign
		rowPath = db.getPathFromRow(row, columns)
		path = os.path.join(savePicturePath, rowPath)
		
		# Get the picture id
		pictureId = db.getValueAtColumn(row, columns, "picture_id")
		
		# Get the collection id by selecting the picture in the database
		pictureCursor = db.selectItemById(connection, pictureId, "picture")
		
		pictureRow = pictureCursor.fetchone()
		pictureColumns = [desc[0] for desc in pictureCursor.description]
		
		collectionId = db.getValueAtColumn(pictureRow, pictureColumns, "collection_id")
		
		# Save the picture in the folder
		try:
			api.savePicture(pictureId, savePicturePath)
			log += "Picture {}.jpeg saved in the saving folder\n".format(pictureId)
		# If the pictuer could not be saved, we skip to the next iteration
		except Exception as e:
			log += "Picture {}.jpeg could not be saved\n".format(pictureId)
			print(e)
			continue
		
		## TO DO : insert code to calculate the position of the cropped sign
		
		## TO DO : insert code to insert geometry of the cropped sign
		
		# Empty the folder
		for item in os.listdir(savePicturePath):
 			itemPath = os.path.join(savePicturePath, item)
 			os.remove(itemPath)
	
	# Save the log into a log file
	with open(os.path.join(logPath, "logFileSignDetection.txt"), 'w') as f:
		f.writelines(log)
	
	# Print how many time it took
	end = time.time()
	print("Saving pictures took {} seconds".format(end - start))