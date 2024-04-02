import requests
import shutil
import json

log = print
# log = lambda *_: ()

def getClosestPictureInformation(lon, lat, dest):
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
	dest : str
		Folder where the picture will be save.

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
		"next_picture_id":"",
		"prev_picture_id":"",
	}
	
	info["coordinates"] = response["features"][0]["geometry"]["coordinates"]
	
	# Check if the picture is a 360° one
	if is360Picture(response["features"][0]["properties"]):
		
		# Save picture in the destination folder
		savePicture(info["sequence_id"], info["picture_id"], dest)
		
		# Save metadata in the destination folder too
		saveMetadata(info, dest)
	
	
	# We search the previous and next picture id
	for link in response["features"][0]["links"]:
		if link["rel"] == "prev":
			info["prev_picture_id"] = link["id"]
		if link["rel"] == "next":
			info["next_picture_id"] = link["id"]
	
	return info, responseTotal

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

def saveMetadata(info, dest):
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
	log(info)
	# Serializing info
	json_object = json.dumps(info, indent=4)
	
	# Save the metadata 
	with open(dest+"/{}.json".format(info["picture_id"]),'w') as f:
		f.write(json_object)
		log("Metadata {} saved in the following folder : \n{}\n".format(info["picture_id"] + ".json", dest))

if __name__=="__main__":
	try:
		response, total = getClosestPictureInformation(4.83534,
												 45.75564,
												 "/home/formation/Documents/TSI/Panoramax")
		
		response, total = getClosestPictureInformation(2.559261111,
												 48.843405556,
												 "/home/formation/Documents/TSI/Panoramax")
	except:
		log("pb")
	response, total = getClosestPictureInformation(7.70989,
											 48.536979,
											 "/home/formation/Documents/TSI/Panoramax")
	
# data = getSequenceData("c4296f2f-ae42-49c9-aa78-8bad2dfceedd")
# print(data)
# fdata = formatSequenceData(data)

# print(fdata)

# with open("out.json", "w") as f:
# 	f.write(json.dumps(fdata))
# make_line(
# make_point("lon", "lat"),
# project(make_point("lon", "lat"),
#  	100,
#  	radians("angle")))