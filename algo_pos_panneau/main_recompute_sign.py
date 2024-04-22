from database_connect import connect_db, DatabaseError
from utils import proj_geo_to_lambert_delta, proj_lambert_delta_to_geo
import pandas as pd
import numpy as np

def load(conn):
    signs = pd.DataFrame([], columns=("id", "lng", "lat", "size", "orientation", "precision", "code", "value"))
    cropped_signs = pd.DataFrame([], columns=("id", "lng", "lat", "sign_id", "sdf", "gisement", "orientation", "code", "value"))
    proj_geo_to_lambert_delta(signs)
    proj_geo_to_lambert_delta(cropped_signs)

    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT s.id, ST_X(s.geom), ST_Y(s.geom), s.size, s.orientation, s.precision, s.code, s.value
                FROM sign AS s
                -- WHERE ST_WITHIN(s.geom, ...)
                """) # TODO: tuillage: complete where constraint
            signs = pd.DataFrame(cur.fetchall(), columns=("id", "lng", "lat", "size", "orientation", "precision", "code", "value"))
            proj_geo_to_lambert_delta(signs)

            cur.execute(f"""
                SELECT c.id, ST_X(p.geom), ST_Y(p.geom), s.id, c.sdf, c.gisement, c.orientation, c.code, c.value
                FROM sign AS s
                JOIN cropped_sign AS c ON c.sign_id = s.id
                JOIN picture AS p ON c.picture_id = p.id
                -- WHERE ST_WITHIN(s.geom, ...)
                """) # TODO: tuillage: complete where constraint
            cropped_signs = pd.DataFrame(cur.fetchall(), columns=("id", "lng", "lat", "sign_id", "sdf", "gisement", "orientation", "code", "value"))
            proj_geo_to_lambert_delta(cropped_signs)

            conn.commit()

            return signs, cropped_signs

    except (Exception, DatabaseError) as error:
        raise error


def recompute_all_signs(signs, cropped_signs):
    pass


def save(conn, signs):
    if len(signs) == 0:
        return
    proj_lambert_delta_to_geo(signs)
    values = ", ".join([
        f"({id}, ST_POINT({lng}, {lat}), {size}, {ori}, {pr}, {code}, {value})"
        for (id, lng, lat, size, ori, pr, code, value) in signs.loc[:, ("id", "lng", "lat", "size", "orientation", "precision", "code", "value")].values
    ])

    try:
        with conn.cursor() as cur:
            cur.execute(f"""UPDATE sign AS s
                        SET geom = new_values.geom, size = new_values.size, orientation = new_values.ori
                            precision = new_values.pr, code = new_values.code, value = new_values.value
                        FROM ( VALUES {values}) AS new_values (id, geom, size, ori, pr, code, value)
                        WHERE s.id = new_values.id;""")
            conn.commit()
    except (Exception, DatabaseError) as error:
        raise error


if __name__ == "__main__":
    print("Connecting to database...\t\t\t", end="")
    conn, config = connect_db()
    print(f"Done")
    
    print("Loading...\t\t\t\t\t", end="")
    signs, cropped_signs = load(conn)
    print(f"Done : {len(signs)} signs, {len(cropped_signs)} cropped_signs")

    print("Computing...\t\t\t\t\t", end="")
    recompute_all_signs(signs, cropped_signs)
    print(f"UNDONE (TODO)")

    print("Saving...\t\t\t\t\t", end="")
    save(conn, signs)
    print(f"Done")

    print("fin")