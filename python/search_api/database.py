import psycopg2
from csv_manager import extractCodeAndValue

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
	linesNumber = 0
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


def selectAll(connection, table, limit=-1):
	"""
	Return the selection in the database for the limited number of lines.

	Parameters
	----------
	connection : psycopg2.extensions.connection
		Database connection token.
	table : psycopg2.extensions.connection
		Name of the table.
	limit : int, optional
		Limit of lines returned. The default is -1.

	Returns
	-------
	None.

	"""
	# Creation of the query
	query = "SELECT * FROM {}".format(table)
	if limit > -1:
		query += " LIMIT {}".format(limit)
	cursor = connection.cursor()
	try:
		# Execute the query
		cursor.execute(query)
	except Exception as e:
		log("The following error occured :", e)
	finally:
		return cursor


def getValueAtColumn(row, columns, name):
	"""
	Given the list of columns, get the value for one column name in a row.

	Parameters
	----------
	row : tuple
		Row of the database.
	columns : list
		List of all column names.
	name : str
		Name of the column to get the value.

	Returns
	-------
	value : any
		Value of the column. Can be an integer, a string...

	"""
	value = row[columns.index(name)]
	return value


def getPathFromRow(row,
				   columns,
				   filenameColumn = "filename",
				   codeColumn = "code",
				   valueColumn = "value"):
	"""
	Return the path of the cropped sign saved in local.

	Parameters
	----------
	row : tuple
		Row of the database.
	columns : list
		List of all column names.
	filenameColumn : str, optional
		Name of the column with the filename. The default is "filename".
	codeColumn : str, optional
		Name of the column with the sign code. The default is "code".
	valueColumn : str, optional
		Name of the column with the sign value. The default is "value".

	Returns
	-------
	path : str
		Path of the cropped sign in local.

	"""
	filename = getValueAtColumn(row, columns, filenameColumn)
	code = getValueAtColumn(row, columns, codeColumn)
	value = getValueAtColumn(row, columns, valueColumn)
	
	# For the moment, only the B14 sign has a value
	if "B14" in code:
		path = "{}-{}/{}".format(code, int(value), filename)
	else:
		path = "{}/{}".format(code, filename)
	
	return path

def croppedSignInDatabase(connection, row, table = "cropped_sign"):
	"""
	Return true if the cropped sign is already in the database

	Parameters
	----------
	connection : psycopg2.extensions.connection
		Database connection token.
	row : tuple
		Row of the database.
	table : str, optional
		Name of the cropped signs table. The default is "cropped_sign".

	Returns
	-------
	isInDB : bool
		True if the cropped sign is already saved into the database.

	"""
	# Extract the filename, code and value from the row
	filename = row["filename"]
	code, value = extractCodeAndValue(row)
	
	# Create and execute the query
	query = """SELECT * FROM {}
		WHERE filename = '{}'
		AND code = '{}'
		AND value = '{}';""".format(table, filename, code, value)
	
	cursor = connection.cursor()
	cursor.execute(query)
	
	# Check the number of rows
	isInDB = (cursor.rowcount > 0)
	
	# Close the cursor
	cursor.close()
	
	return isInDB

def itemAlreadyInDatabase(connection, itemId, table):
	"""
	Return true if the item is already saved in the table.

	Parameters
	----------
	connection : psycopg2.extensions.connection
		Database connection token.
	itemId : str
		Id of the item.
	table : str
		Name of the table containing the item.

	Returns
	-------
	isInDB : bool
		True if the picture is already saved into the database.

	"""
	# Create and execute the query
	query = "SELECT * FROM {} WHERE id = '{}'".format(table, itemId)
	cursor = connection.cursor()
	cursor.execute(query)
	
	# Check the number of rows
	isInDB = (cursor.rowcount > 0)
	
	# Close the cursor
	cursor.close()
	
	return isInDB

def updateCenterOfSign(connection, id, x, y, dz, table = "cropped_sign"):
	"""
	Update the position if the picture of the cropped sign, with the good id.

	Parameters
	----------
	connection : psycopg2.extensions.connection
		Database connection token.
	id : str
		Id of the cropped sign.
	x : int
		X position of the center of the sign in the original picture.
	y : int
		X position of the center of the sign in the original picture.
	dz : float
		Height of the sign in the original picture.
	table : str, optional
		Name of the cropped sign table. The default is "cropped_sign".

	Returns
	-------
	linesNumber : int
		Number of lines affected by the query.

	"""
	# Create the query
	query = """UPDATE {} SET x={}, y={}, dz={}
	WHERE id = '{}';""".format(table, x, y, dz, id)
	
	linesNumber = 0
	try:
		# Execute and commit the query
		cursor = connection.cursor()
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
	