import requests
import shutil
import json
import psycopg2
import pandas as pd

log = print

def getConnection(host,
				  user="postgres",
				  password="postgres",
				  port="5432",
				  database="panneaux"):
	"""
	Get connection token to the database.
	Only the host is required, other parameters can be ommited.

	Parameters
	----------
	host : str
		Ip address for the database connection.
	user : str, optional
		Username for the database connection. The default is "postgres".
	password : str, optional
		Password for the database connection. The default is "postgres".
	port : str, optional
		Port for the connection. The default is "5432".
	database : str, optional
		Database to connect to. The default is "panoramax".

	Returns
	-------
	connection : psycopg2.extensions.connection
		Database connection token.

	"""
	connection = psycopg2.connect(host=host,
								  user=user,
								  password=password,
								  port=port,
								  database=database)
	return connection

def insertQuery(connection, query):
	"""
	Insert a row in a database, where the query is already formated.
	It returns the number of lines affected by the query.

	Parameters
	----------
	connection : psycopg2.extensions.connection
		Database connection token.
	query : str
		Insert query already formatted.

	Returns
	-------
	linesNumber : int
		Number of lines affected by the query.

	"""
	linesNumber= 0
	try:
		cursor = connection.cursor()
		# Execute and commit the query
		cursor.execute(query)
		connection.commit()
		linesNumber = cursor.rowcount
	except Exception as e:
	    # If there is an error, the transaction is canceled
	    connection.rollback()
	    log("The following error occured :", e)
	finally:
		# The transaction is closed anyway
		cursor.close()
		return linesNumber


def readCSVFile(path):
	"""
	Read a CSV file into a pandas dataframe

	Parameters
	----------
	path : str
		Relatiive path of the file.

	Returns
	-------
	dataframe : pandas.dataframe.
		Dataframe of the csv file

	"""
	data = pd.read_csv(path, delimiter = ";")
	return data

def extractCodeAndValue(row):
	"""
	Extract the code of the sign and the value if necessary.

	Parameters
	----------
	row : pandas.core.series.Series
		Line of the read csv file.

	Returns
	-------
	code : str
		Code of the sign.
	value : str
		None if the sign has no value. Otherwise, correspond to the sign value

	"""
	directory = row["directory"]
	code = directory[15::]
	if "B14" in code:
		value = code[4::]
		code = code[0:3]
	else:
		value = "null"
	return code, value

def reformatBbox(row):
	"""
	Reformat the bbox in the appropriate format.

	Parameters
	----------
	row : pandas.core.series.Series
		Line of the read csv file.

	Returns
	-------
	bbox : str
		Bbox of the sign in the picture.

	"""
	comment = json.loads(row["comment"])
	[x, y, w, h] = list(comment["xywh"])
	bbox = "[{},{},{},{}]".format(x, y, x + w, y + h)
	return bbox

def getClosestPictureInformation(lon, lat):
	"""
	This function get the closest picture using the search API.
	It also save the picture and the usefull metadata in the
	destination folder.

	Parameters
	----------
	lon : float
		Point of interest longitude.
	lat : float
		Point of interest latitude.

	Returns
	-------
	info : dict.
		Information about the picture.
	"""
	url = "https://api.panoramax.xyz/api/search"
	
	# Data for the post request
	dataToSend = {
		"limit":1,
	}
	
	bbox = "{},{},{},{}".format(round(lon - 0.00001, 5),
							 round(lat - 0.00001, 5),
							 round(lon + 0.00001, 5),
							 round(lat + 0.00001, 5))
	
	dataToSend["bbox"] = bbox
	log(url+"?limit=1&bbox={}".format(bbox))
	
	# Send and get the answer of the file
	responseTotal = requests.post(url, json=dataToSend)
	response = responseTotal.json()
	
	# If there is no answer, an exception is raised
	if len(response["features"]) == 0:
		raise requests.exceptions.RequestException()
	
	
	# Usefull information
	info = {
		"sequence_id":response["features"][0]["collection"],
		"picture_id":response["features"][0]["id"],
		"lon_picture":response["features"][0]["geometry"]["coordinates"][0],
		"lat_picture":response["features"][0]["geometry"]["coordinates"][1],
		"is360picture":""
	}
	
	info["is360picture"] = is360Picture(response["features"][0]["properties"])
	
	return info

def is360Picture(properties):
	"""
	Return true if the picture is a 360 one.

	Parameters
	----------
	properties : dict
		Properties of the picture.

	Returns
	-------
	test : bool
		True if the picture is a 360 one.

	"""
	# We initiate the test to false
	test = False
	
	# Try and catch is necessary because the field of view is not always in the data
	try:
		if properties["pers:interior_orientation"]["field_of_view"] == 360:
			test = True
	finally:
		return test
	

def savePicture(sequence_id, picture_id, dest):
	"""
	Save the picture in HD in the destination folder.
	It also saves the metadata linked to the image.

	Parameters
	----------
	sequence_id : str
		Id of the sequence.
	picture_id : str
		Id of the picture.
	dest : str
		Folder where the picture will be save.

	Returns
	-------
	None.

	"""
	# Get the picture
	picture_url = "https://api.panoramax.xyz/api/pictures/{}/hd.jpg".format(picture_id)
	picture_response = requests.get(picture_url, stream = True)
	
	# Save the picture 
	if picture_response.status_code == 200:
		with open(dest+"/{}.jpeg".format(picture_id),'wb') as f:
			shutil.copyfileobj(picture_response.raw, f)
			log("Picture {} saved in the following folder : \n{}\n".format(picture_id + ".jpeg", dest))


if __name__=="__main__":
	try:
		response = getClosestPictureInformation(4.83534, 45.75564)
		response = getClosestPictureInformation(2.559261111, 48.843405556)
	except:
		log("pb")
	response = getClosestPictureInformation(7.70989, 48.536979)


if __name__=="__main__":
	dataframe = readCSVFile("../../exif_data.csv")
