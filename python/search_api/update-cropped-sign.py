import os
import database as db
import time

if __name__ == "__main__":
	
	# Time of the algorithm
	start = time.time()
	
	# Add a log to save the result in a log file
	log = ""
	logPath = "/home/formation/Documents/TSI/Panoramax/log"
	
	# Path of all the cropped sign
	croppedSignPath = "/home/formation/Documents/TSI/Panoramax/pictures"
	
	# Get the connection - "172.31.58.179, password = "tsi23lesboss",
	connection = db.getConnection("127.0.0.1", 
							   database="panoramax")
	
	# Select all lines and get the column names
	cursor = db.selectAll(connection, "cropped_sign")
	columns = [desc[0] for desc in cursor.description]
	
	# Browse all lines of the database
	for index, row in enumerate(cursor.fetchall()):
		# Get the path of the relative path of the cropped sign
		rowPath = db.getPathFromRow(row, columns)
		path = os.path.join(croppedSignPath, rowPath)
		
		# Initialise x, y and dz to null values
		x, y, dz = "null", "null", "null"
		
		# Calculate the center of the cropped sign
		
		## TO DO : INSERT CODE TO CALCULATE THE CENTER OF THE CROPPED SIGN
		
		# Calculate the height of the cropped sign
		
		## TO DO : INSERT CODE TO CALCULATE THE HEIGHT OF THE CROPPED SIGN
		
		# Update the cropped sign attributes in the database
		croppedSignId = db.getValueAtColumn(row, columns, "id")
		linesUpdated = db.updateCenterOfSign(connection, croppedSignId, x, y, dz)
		
		if linesUpdated == 0:
			log += "No lines where updated for the cropped sign {}\n".format(rowPath)
		else:
			log += "Values for the cropped sign {} has been updated\n".format(rowPath)
	
	# Save the log into a log file
	with open(os.path.join(logPath, "logFileUpdate.txt"), 'w') as f:
		f.writelines(log)
	
	end = time.time()
	print("The update took {} seconds".format(end - start))