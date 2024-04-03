from configparser import ConfigParser
import psycopg2
import pandas as pd

__path__ = "/".join(__file__.split("/")[:-1])

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
    values = ",".join([struct.format(*line) for line in list(data)]).replace("'None'", "NULL")
    return f'''
        INSERT INTO {pg_table} ({",".join(pg_columns)})
        VALUES {values}'''


def init_tests():
    assert "test" in _config["database"]
    seq_id = "a957f734-e816-4c1d-af36-7f35deea2b78"
    photo = pd.read_csv(__path__ + "/../../data_test/cropped_signs/photo.csv")
    imagette = pd.read_csv(__path__ + "/../../data_test/cropped_signs/imagette.csv")
    photo["id_seq"] = seq_id
    #print(photo.loc[1:0])
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
        print(error)


def init():
    global imagette, panneau, photo, sequence
    imagette = pd.DataFrame()
    panneau = pd.DataFrame()
    photo = pd.DataFrame()
    sequence = pd.DataFrame()

_config = _load_config()
conn = _connect(_config)

# init_tests()