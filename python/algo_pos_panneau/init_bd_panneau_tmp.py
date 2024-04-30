import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from algo_pos_panneau.database_connect import connect_db, df_to_insert, DatabaseError
import pandas as pd

__path__ = "/".join(__file__.split("/")[:-1])

###############################################################################
##  Database initialisation                                                  ##
###############################################################################

def init_tests(conn, config):
    assert "test" in config["database"]    # verify that config is for test
    seq_id = "a957f734-e816-4c1d-af36-7f35deea2b78"
    photo = pd.read_csv(__path__ + "/../../useful_data/data_test/cropped_signs/photo.csv")
    imagette = pd.read_csv(__path__ + "/../../useful_data/data_test/cropped_signs/imagette.csv").replace({"A0-A":"A00", "A0-B":"A00"})
    photo["id_seq"] = seq_id
    photo["width"] = 5760
    photo["height"] = 2880
    imagette["value"] = "30"
    imagette.loc[imagette.code!="B14", ("value")] = None
    try:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE collection, cropped_sign, picture, sign RESTART IDENTITY")
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
    except (Exception, DatabaseError) as error:
        raise error

###############################################################################
##  Start                                                                    ##
###############################################################################

if __name__ == "__main__":
    print("Connect to database...\t", end="")
    conn, config = connect_db()
    print("Done")

    print("Format database...\t", end="")
    init_tests(conn, config)
    print("Done")

    print("End")