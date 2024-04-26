from python.search_api import database

connx = database.getConnection('localhost')

def test_getConnection():
    assert(connx != None)

def test_insertQuery():
    query = "CREATE TABLE test  (id INT, name VARCHAR(255))"
    database.insertQuery(connx, query)
    query = "INSERT INTO test (id, name) VALUES (1, 'test')"
    database.insertQuery(connx, query)

def test_getValueAtColumn():
    row = ('168131','C12',43.118,7.7412)
    columns = ['id','code','latitude','longitude']
    assert(database.getValueAtColumn(row,columns,'code') == 'C12')

def test_updateCenterOfSign():
    query = "CREATE TABLE cropped_sign(id INT, x INT, y INT, filename VARCHAR(255))"
    database.insertQuery(connx, query)
    query = "INSERT INTO cropped_sign (id, x, y,filename) VALUES (1, 10, 10, 'test.jpg')"
    database.insertQuery(connx, query)
    cursor1 = database.selectCroppedSignByFilename(connx, 'test.jpg')
    database.updateCenterOfSign(connx, cursor1, 20, 20, 5)
    cursor2 = database.selectCroppedSignByFilename(connx, 'test.jpg')
    assert(cursor1 != cursor2)

def test_itemAlreadyInDatabase():
    assert(database.itemAlreadyInDatabase(connx, 1, 'cropped_sign') == True)

if __name__ == "__main__":
    import pytest
    pytest.main(["-v", __file__])
