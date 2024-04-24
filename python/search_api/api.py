import requests
import shutil
from PIL import Image
from io import BytesIO


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
	# url = "https://panoramax.ign.fr/api/search"

	# Data for the post request
	dataToSend = {
		"limit": 1,
	}

	# Bbox centered on the picture

	bbox = "{},{},{},{}".format(lon - 0.00001,
								lat - 0.00001,
								lon + 0.00001,
								lat + 0.00001)
	dataToSend["bbox"] = bbox

	# Send and get the answer of the file
	responseTotal = requests.post(url, json=dataToSend)
	response = responseTotal.json()

	# If there is no answer, an exception is raised
	if len(response["features"]) == 0:
		raise requests.exceptions.RequestException()

	# Usefull information
	info = {
		"collectionId": response["features"][0]["collection"],
		"pictureId": response["features"][0]["id"],
		"lonPicture": response["features"][0]["geometry"]["coordinates"][0],
		"latPicture": response["features"][0]["geometry"]["coordinates"][1],
		"is360picture": ""
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


def getShapePicture(pictureId):
	"""
	Get the shape of a picture (width, height).
	It uses the Pictures API of Panoramax

	Parameters
	----------
	pictureId : str
		Id of the picture.

	Returns
	-------
	None.

	"""
	url = "https://api.panoramax.xyz/api/pictures/{}/hd.jpg".format(pictureId)
	response = requests.get(url, stream=True)

	# Check the status code
	if response.status_code == 200:
		# Get the picture without saving it
	    picture = Image.open(BytesIO(response.content))
	    
	    # Get the size of the picture
	    width, height = picture.size
	
	return (width, height)


def savePicture(pictureId, dest):
	"""
	Save the picture in HD in the destination folder.
	It also saves the metadata linked to the image.

	Parameters
	----------
	collectionId : str
		Id of the collection.
	pictureId : str
		Id of the picture.
	dest : str
		Folder where the picture will be save.

	Returns
	-------
	None.

	"""
	# Get the picture
	pictureUrl = "https://api.panoramax.xyz/api/pictures/{}/hd.jpg".format(pictureId)
	pictureResponse = requests.get(pictureUrl, stream=True)

	# Save the picture
	if pictureResponse.status_code == 200:
		with open(dest+"/{}.jpeg".format(pictureId), 'wb') as f:
			shutil.copyfileobj(pictureResponse.raw, f)


def savePictures(collectionId, pictureId, dest):
	"""
	Save the picture, the next and the previous one only if they exist.
	If they do not exist, none of them will be downloaded.

	Parameters
	----------
	collectionId : str
		Id of the collection.
	pictureId : str
		Id of the picture.
	dest : str
		Folder where the picture will be save.

	Returns
	-------
	None.

	"""
