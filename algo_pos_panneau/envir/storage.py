from configparser import ConfigParser
import psycopg2
import pandas as pd

__path__ = "/".join(__file__.split("/")[:-1])

###############################################################################
##  Database connection                                                      ##
###############################################################################

def _load_config(filename=__path__ + "/database.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)
    
    # get section, default to postgresql
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))
    return config

def _connect(config):
    """ Connect to the PostgreSQL database server """
    try:
        # connecting to the PostgreSQL server
        with psycopg2.connect(**config) as conn:
            print('Connected to the PostgreSQL server.')
            return conn
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

def df_to_insert(df, df_keys, struct, pg_table, pg_columns):
    data = df.loc[:, df_keys].values
    values = ",".join([struct.format(*line) for line in list(data)]).replace("'None'", "NULL").replace("'nan'", "NULL").replace("nan", "NULL").replace("None", "NULL")
    return f'''
        INSERT INTO {pg_table} ({",".join(pg_columns)})
        VALUES {values}'''

###############################################################################
##  Database initialisation                                                  ##
###############################################################################

def init_tests():
    assert "test" in _config["database"]
    seq_id = "a957f734-e816-4c1d-af36-7f35deea2b78"
    photo = pd.read_csv(__path__ + "/../../data_test/cropped_signs/photo.csv")
    imagette = pd.read_csv(__path__ + "/../../data_test/cropped_signs/imagette.csv")
    photo["id_seq"] = seq_id
    photo["width"] = 5760
    photo["height"] = 2880
    imagette["value"] = "30"
    imagette.loc[imagette.code!="B14", ("value")] = None
    try:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE imagette, panneau, photo, sequence")
            cur.execute(f"INSERT INTO sequence (id, date) VALUES ('{seq_id}', '01/01/2024')")

            cur.execute(df_to_insert(
                photo,
                ("id", "id_seq", "lat", "lng", "azimut", "fov", "width", "height", "href"),
                "('{0}', '{1}', ST_POINT({3}, {2}, 4326), {4}, {5}, {6}, {7}, '{8}')",
                "photo",
                ("id", "id_sequence", "geom", "azimut", "fov", "width", "height", "href")
            ))

            cur.execute(df_to_insert(
                imagette,
                ("id", "source", "x", "y", "dz", "code", "value"),
                "('{0}', '{1}', {2}, {3}, {4}, '{5}', '{6}')",
                "imagette",
                ("id", "id_photo", "x", "y", "dz", "code", "value")
            ))

            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        raise error

###############################################################################
##  Data management                                                          ##
###############################################################################

def get_sequence_ids(limit=10):
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT id FROM sequence LIMIT {limit}")
            return [l[0] for l in cur.fetchall()]
    except (Exception, psycopg2.DatabaseError) as error:
        raise error

def select_from_sequence(id_sequence):
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT id, date FROM sequence WHERE id = '{id_sequence}'")
            sequence = pd.DataFrame(cur.fetchall(), columns=("id", "date"))
            
            cur.execute(f"SELECT id, id_sequence, ST_Y(geom) AS lat, ST_X(geom) AS lng, azimut, width, height, fov, href FROM photo WHERE id_sequence = '{id_sequence}'")
            photo = pd.DataFrame(cur.fetchall(), columns=("id", "id_sequence", "lat", "lng", "azimut", "width", "height", "fov", "href"))
            
            cur.execute(f"""SELECT i.id, i.id_photo, i.id_panneau, i.x, i.y, i.dz, i.code, i.value,
            	ST_Y(geom_estim) AS lat, ST_X(i.geom_estim) AS lng
	            FROM photo AS p 
	            JOIN imagette AS i ON i.id_photo = p.id
	            WHERE p.id_sequence = '{id_sequence}'""")
            imagette = pd.DataFrame(cur.fetchall(), columns=("id", "id_photo", "id_panneau", "x", "y", "dz", "code", "value", "lat", "lng"))

            cur.execute(f"""SELECT pa.id, ST_Y(pa.geom) AS lat, ST_X(pa.geom) AS lng, pa.size, 
                pa.orientation, pa.precision, pa.code, pa.value
                FROM photo AS p 
                JOIN imagette AS i ON i.id_photo = p.id
                JOIN panneau AS pa ON pa.id = i.id_panneau
                WHERE p.id_sequence = '{id_sequence}'""")
            panneau = pd.DataFrame(cur.fetchall(), columns=("id", "lat", "lng", "size", "orientation", "precision", "code", "value"))

            return [sequence, photo,imagette,panneau]
    except (Exception, psycopg2.DatabaseError) as error:
        raise error
    
def update_imagette(imagette):
    try:
        with conn.cursor() as cur:
            data = imagette.loc[:, ("id", "id_photo", "id_panneau", "x", "y", "dz", "code", "value", "lat", "lng")].values
            for line in data:
                query = """
                UPDATE imagette SET id_photo='{1}', id_panneau='{2}', x={3}, y={4}, dz={5},
                    code='{6}', value='{7}', geom_estim = ST_POINT({9}, {8}, 4326)
                WHERE id='{0}'
                """.format(*line).replace("'None'", "NULL")
                cur.execute(query)
            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        raise error
    
def get_new_unique_id_panneau(increment=True):
    try:
        with conn.cursor() as cur:
            fonc = "NEXTVAL" if increment else "CURRVAL"
            cur.execute(f"SELECT {fonc}(PG_GET_SERIAL_SEQUENCE('panneau', 'id'))")
            conn.commit()
            id = cur.fetchone()[0]
            return id
    except (Exception, psycopg2.DatabaseError) as error:
        raise error

def update_panneau(panneau):
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT id FROM panneau WHERE id IN ({','.join(map(str, panneau.id.values))})")
            ids = cur.fetchall()
            print("0", ids)
            # revoir ces extractions
            panneau_update = panneau.set_index("id").loc[ids]
            print("1")
            panneau_insert = panneau.set_index("id").loc[panneau.index.difference(ids)]
            print("2")

            data = panneau_update.loc[:, ("id", "lat", "lng", "size", "orientation", "precision", "code", "value")].values
            for line in data:
                query = """
                UPDATE panneau SET geom=ST_POINT({2}, {1}, 4326), size={3}, orientation={4}, precision={5}, code='{6}', value='{7}'
                WHERE id='{0}'
                """.format(*line).replace("'None'", "NULL")
                cur.execute(query)
            conn.commit()

            cur.execute(df_to_insert(
                panneau_insert,
                ("id", "lat", "lng", "size", "orientation", "precision", "code", "value"),
                "({0}, ST_POINT({2}, {1}, 4326), {3}, {4}, {5}, '{6}', '{7}')",
                "panneau",
                ("id", "geom", "size", "orientation", "precision", "code", "value")
            ))
            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        raise error

###############################################################################
##  Start                                                                    ##
###############################################################################

_config = _load_config()
conn = _connect(_config)

#init_tests()
