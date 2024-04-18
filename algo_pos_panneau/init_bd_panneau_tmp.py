from database_connect import conn, df_to_insert, _config
import pandas as pd

__path__ = "/".join(__file__.split("/")[:-1])

###############################################################################
##  Database initialisation                                                  ##
###############################################################################

def init_tests():
    assert "test" in _config["database"]    # verify that config is for test
    seq_id = "a957f734-e816-4c1d-af36-7f35deea2b78"
    photo = pd.read_csv(__path__ + "/../data_test/cropped_signs/photo.csv")
    imagette = pd.read_csv(__path__ + "/../data_test/cropped_signs/imagette.csv")
    photo["id_seq"] = seq_id
    photo["width"] = 5760
    photo["height"] = 2880
    imagette["value"] = "30"
    imagette.loc[imagette.code!="B14", ("value")] = None
    try:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE collection, cropped_sign, picture, sign")
            cur.execute(f"INSERT INTO collection (id, date) VALUES ('{seq_id}', '01/01/2024')")

            cur.execute(df_to_insert(
                photo,
                ("id", "id_seq", "lat", "lng", "azimut", "fov", "width", "height"),
                "('{0}', '{1}', ST_POINT({3}, {2}, 4326), {4}, {5}, {6}, {7}, 'unknown')",
                "picture",
                ("id", "collection_id", "geom", "azimut", "fov", "width", "height", "model")
            ))

            cur.execute(df_to_insert(
                imagette,
                ("id", "source", "x", "y", "dz", "code", "value"),
                "('{1}', {2}, {3}, {4}, '{5}', '{6}', 'nofilename')",
                "cropped_sign",
                ("picture_id", "x", "y", "dz", "code", "value", "filename")
            ))

            conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        raise error

###############################################################################
##  Start                                                                    ##
###############################################################################

if __name__ == "__main__":
    init_tests()
