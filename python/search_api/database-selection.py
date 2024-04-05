import api
import database as db

if __name__ == "__main__":
	# Get the connection
	connection = db.getConnection("127.0.0.1")
	
	# Select all lines and get the column names
	cursor = db.selectAll(connection, "panneaux")
	
	columns = [desc[0] for desc in cursor.description]
	
	for row in cursor:

		filename = db.getValueAtColumn(row, columns, "filename")
		code = db.getValueAtColumn(row, columns, "code")
		if "B14" in code:
			path = db.getPathFromRow(row, columns)
			break

	print(db.itemAlreadyInDatabase(connection, 1, "panneaux"))
	
	
