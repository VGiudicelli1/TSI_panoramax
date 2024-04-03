import api
from datetime import datetime

if __name__=="__main__":
	# Read the csv file
	csvPath = "../data/exif_data.csv"
	data = api.readCSVFile(csvPath)
	
	# Get the connection and create the general insert query
	connection = api.getConnection("127.0.0.1")

	insert_query = """INSERT INTO public.panneaux(
	filename, code, value, datetime, camera_model, gpsimagedirection, bbox_in_picture, lon_picture, lat_picture, sequence_id, picture_id)
	VALUES ('{filename}',
		 '{code}',
		 {value},
		 '{datetime}',
		 '{camera_model}',
		 {gpsimagedirection},
		 '{bbox_in_picture}',
		 {lon_picture},
		 {lat_picture},
		 '{sequence_id}',
		 '{picture_id}');"""
	
	# Dictionnary used after to fill the query
	value_query = {
		"filename":"",
		"code":"",
		"value":"",
		"datetime":"",
		"camera_model":"",
		"gpsimagedirection":"",
		"bbox_in_picture":"",
		"lon_picture":"",
		"lat_picture":"",
		"sequence_id":"",
		"picture_id":""
		}
	
	# Go through every line of the csv
	for index, row in data.iterrows():
		# Get the first information directly from the csv
		value_query["filename"] = row["filename"]
		value_query["camera_model"] = row["model"]
		value_query["gpsimagedirection"] = row["gpsimagedirection"]
		
		# Transform information from the csv file
		# Transform the string date into a datetime object
		value_query["datetime"] = datetime.strptime(row["date"], "%Y:%m:%d%H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
		
		code, value = api.extractCodeAndValue(row)
		value_query["code"] = code
		value_query["value"] = value
		
		bbox = api.reformatBbox(row)
		value_query["bbox_in_picture"] = bbox
		
		# Request the Search API to find information about the picture
		info = api.getClosestPictureInformation(row["lon"], row["lat"])
		
		value_query["lon_picture"] = info["lon_picture"]
		value_query["lat_picture"] = info["lat_picture"]
		value_query["sequence_id"] = info["sequence_id"]
		value_query["picture_id"] = info["picture_id"]
		
		is360picture = info["is360picture"]
		
		# If the picture is a 360 one, we save it
		if is360picture:
			# Creation of the query
			query = insert_query.format(**value_query)
			
			# Execution of the query and result print
			linesNumber = api.insertQuery(connection, query)
			if linesNumber > 0:
				print("Information about picture {}/{} has been inserted in the database.".format(code, row["filename"]))
			
		else:
			print("The picture {}/{} is not a 360 image. It will not be downloaded.".format(code, row["filename"]))
