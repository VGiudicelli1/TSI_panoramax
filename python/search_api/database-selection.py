import api
import database as db

if __name__ == "__main__":
	# Get the connection
	# Mutual database connection :  "172.31.58.179", password = "tsi23lesboss",
	connection = db.getConnection("127.0.0.1", 
							   database="panoramax")
	
	# Select all lines and get the column names
	# cursor = db.selectAll(connection, "cropped_sign")
	
	
	cursor = db.selectCroppedSignByFilename(connection, "01d7d4010541dfc5eaa5b6d87b58ec5efca8bfcf04a79e529b42f0702ef9a4fd.jpg")
	
	columns = [desc[0] for desc in cursor.description]
	
	if cursor.rowcount == 0:
		print("No cropped sign")
	elif cursor.rowcount > 1:
		print("Too many cropped sign")
	else:
		row = cursor.fetchone()
		id = db.getValueAtColumn(row, columns, "id")
		lines = db.updateCenterOfSign(connection, id, 1125, 125, 60)
		print(lines)
	
	
	
