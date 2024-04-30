import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from algo_pos_panneau.database_connect import connect_db, DatabaseError
from algo_pos_panneau.utils import proj_geo_to_lambert_delta, proj_lambert_delta_to_geo, mean_angles_deg
import pandas as pd
import numpy as np
import math
from algo_pos_panneau.code_panneaux import is_code_face

def load(conn):
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


def recompute_sign(id, signs, cropped_signs):
    cs = cropped_signs.loc[cropped_signs.sign_id == id]

    # code, valeur: minimum 3 from face
    codes = [ (code, value) for (value, code) in cs.loc[:, ("value", "code")].values if is_code_face(code)]
    if len(codes) < 3:
        return

    # e, n, size: par moindre carrés
    n = len(cs)
    A = np.zeros((2*n, 3))
    B = np.zeros((2*n, 1))

    B[0::2, 0] = cs.e
    B[1::2, 0] = cs.n

    A[0::2, 0] = 1
    A[1::2, 1] = 1
    A[0::2, 2] = -cs.sdf * np.sin(cs.gisement * math.pi / 180)
    A[1::2, 2] = -cs.sdf * np.cos(cs.gisement * math.pi / 180)

    X = np.linalg.lstsq(A, B, rcond=None)[0]

    signs.loc[signs.id==id, ("e", "n", "size")] = X.reshape(3)
    signs.loc[signs.id==id, "orientation"] = mean_angles_deg(cs.orientation)
    signs.loc[signs.id==id, ("code", "value")] = codes[0]


def recompute_all_signs(signs, cropped_signs):
    for id in signs.loc[:, "id"].values:
        recompute_sign(id, signs, cropped_signs)


def save(conn, signs):
    if len(signs) == 0:
        return
    proj_lambert_delta_to_geo(signs)
    values = ", ".join([
        f"({id}, ST_POINT({lng}, {lat}), {size}, {ori}, {pr}, '{code}', '{value}')".replace("'None'", "NULL").replace("'null'", "NULL")
        for (id, lng, lat, size, ori, pr, code, value) in signs.loc[:, ("id", "lng", "lat", "size", "orientation", "precision", "code", "value")].values
    ])

    try:
        with conn.cursor() as cur:
            cur.execute(f"""UPDATE sign AS s
                        SET geom = new_values.geom, size = new_values.size, orientation = new_values.ori,
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
    print(f"Done")

    print("Saving...\t\t\t\t\t", end="")
    save(conn, signs)
    print(f"Done")

    print("fin")
