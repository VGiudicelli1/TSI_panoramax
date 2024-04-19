import pandas as pd
import json
from datetime import datetime, timedelta


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
	data = pd.read_csv(path, delimiter=";")
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
	code = row["directory"]
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


def getIntervalFromDate(date, seconds):
	"""
	Returns an interval centered on the datetime.
	The number of seconds before and after the date is given in the parameter.

	Parameters
	----------
	datetime : str
		Date of the interval.
	seconds : int
		Seconds necessary for the interval.

	Returns
	-------
	dateBefore : str
		Minimum date of the interval.
	dateAfter : str
		Maximum date of the interval.

	"""
	# Convert the string in an datetime object
	dateObj = datetime.strptime(date, "%Y:%m:%d%H:%M:%S")

	# 5 seconds interval
	interval = timedelta(seconds=seconds)

	# Calcul of the date before and after
	dateBefore = dateObj - interval
	dateAfter = dateObj + interval

	# Reformat of the date
	dateBefore = dateBefore.strftime("%Y-%m-%dT%H:%M:%SZ")
	dateAfter = dateAfter.strftime("%Y-%m-%dT%H:%M:%SZ")

	return dateBefore, dateAfter
