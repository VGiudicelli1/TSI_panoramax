import api
import database as db
import csv_manager as csv
from datetime import datetime

# Template insert query for the different tables
insertQueryCollection = """INSERT INTO public.collection(
	id, date)
	VALUES ('{collectionId}', '{collectionDate}');"""

insertQueryPicture = """INSERT INTO public.picture(
	id, collection_id, geom, azimut, width, height, fov, model)
	VALUES ('{pictureId}',
		 '{collectionId}',
		 ST_SetSRID(ST_MakePoint({lonPicture}, {latPicture}), 4326),
		 {azimut},
		 {width},
		 {height},
		 {fov},
		 '{model}');"""

insertQueryCroppedSign = """INSERT INTO public.cropped_sign(
	picture_id, filename, bbox, code, value)
	VALUES ('{pictureId}',
		 '{filename}',
		 '{bbox}',
		 '{code}',
		 '{value}');"""

# Value of the different columns, all put in one dictionnary
valueQuery = {
		"collectionId": "",
		"collectionDate": "",
		"pictureId": "",
		"lonPicture": "",
		"latPicture": "",
		"azimut": "",
		"width": "",
		"height": "",
		"fov": "",
		"model": "",
		"filename": "",
		"bbox": "",
		"code": "",
		"value": ""
	}

if __name__ == "__main__":
	# Read the csv file
	csvPath = "../../data/exif_data.csv"
	data = csv.readCSVFile(csvPath)

	nonTreatedPictures = ""

	# Get the connection and create the general insert query
	connection = db.getConnection("127.0.0.1")

	# Go through every line of the csv
	for index, row in data.iterrows():
		
		# If the cropped sign is already registered, we skip to the next line
		if db.croppedSignInDatabase(connection, row):
			print("Picture {}/{} is already registered in the database".
		 format(row["directory"], row["filename"]))
			continue
		
		# Get the first information directly from the csv
		valueQuery["filename"] = row["filename"]
		valueQuery["model"] = row["model"]
		valueQuery["azimut"] = row["gpsimagedirection"]

		## Transform information from the csv file
		# Transform the string date into a datetime object
		valueQuery["collectionDate"] = datetime.strptime(row["date"], "%Y:%m:%d%H:%M:%S").strftime("%Y-%m-%d")
		
		# Get the code and value of the sign
		valueQuery["code"], valueQuery["value"] = csv.extractCodeAndValue(row)
		
		# Reformat the bbox to be in the good format
		valueQuery["bbox"] = csv.reformatBbox(row)

		try:
			# Request the Search API to find information about the picture
			info = api.getClosestPictureInformation(row["lon"], row["lat"])
			
			valueQuery["lonPicture"] = info["lonPicture"]
			valueQuery["latPicture"] = info["latPicture"]
			valueQuery["collectionId"] = info["collectionId"]
			valueQuery["pictureId"] = info["pictureId"]
			valueQuery["width"], valueQuery["height"] = api.getShapePicture(info["pictureId"])

			is360picture = info["is360picture"]

			# If the picture is a 360 one, we save 360 as the field of view
			if is360picture:
				valueQuery["fov"] = 360
			else:
				valueQuery["fov"] = "null"
			
			
			## Test if the collection or the picture are already registered
			# Collection
			collectionInDb = db.itemAlreadyInDatabase(connection,
											 valueQuery["collectionId"],
											 "collection")
			
			if not collectionInDb:
				collectionQuery = insertQueryCollection.format(**valueQuery)
				linesNumber = db.insertQuery(connection, collectionQuery)
				if linesNumber > 0:
					print("Collection {} inserted".
		   format(valueQuery["collectionId"]))
						
			# Picture
			pictureInDb = db.itemAlreadyInDatabase(connection,
											 valueQuery["pictureId"],
											 "picture")
			
			if not pictureInDb:
				pictureQuery = insertQueryPicture.format(**valueQuery)
				linesNumber = db.insertQuery(connection, pictureQuery)
				if linesNumber > 0:
					print("Picture {} inserted".
		   format(valueQuery["pictureId"]))
			
			# Save the cropped sign in the database
			croppedSignQuery = insertQueryCroppedSign.format(**valueQuery)
			linesNumber = db.insertQuery(connection, croppedSignQuery)
			if linesNumber > 0:
				print("Cropped sign {}/{} inserted".
		  format(row["directory"], row["filename"]))
			
		except Exception as e:
			nonTreatedPictures += "{}/{}\n".format(row["directory"], row["filename"])
			print("No features found for the following picture : {}/{}".
		 format(row["directory"], row["filename"]))

	# We save into files the non registered pictures
	with open("../../../nonTreatedPictures.txt", 'w') as f:
		f.writelines(nonTreatedPictures)