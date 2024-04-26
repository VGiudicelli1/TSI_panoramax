import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from algo_pos_panneau.database_connect import connect_db, DatabaseError
import pandas as pd
from math import pi
import numpy as np
from algo_pos_panneau.utils import format_angle_deg
"""
compute gisement and sdf
need:
id, x, y, dz, source_width, source_height, source_fov, source_azimut
"""

def load(conn):
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT c.id, c.x, c.y, c.dz, p.width, p.height, p.fov, p.azimut
	            FROM picture AS p 
	            JOIN cropped_sign AS c ON c.picture_id = p.id
                WHERE c.x IS NOT NULL 
                    AND c.y IS NOT NULL 
                    AND c.dz IS NOT NULL
                    AND c.dz > 0 -- when dz=0, sdf=inf
                    AND p.width IS NOT NULL 
                    AND p.height IS NOT NULL 
                    AND p.fov IS NOT NULL 
                    AND p.azimut IS NOT NULL
                    AND (c.sdf IS NULL OR c.gisement IS NULL)
                """)
            detections = pd.DataFrame(cur.fetchall(), columns=("id", "x", "y", "dz", "source_width", "source_height", "source_fov", "source_azimut"))

            conn.commit()

            return detections
    except (Exception, DatabaseError) as error:
        raise error
    
def save(conn, data):
    if len(data) == 0:
        return
    values = data.loc[:, ("id", "sdf", "gisement", "orientation")].values
    values_sql = ", ".join([f"({id}, {sdf}, {gis}, {orient})" for (id, sdf, gis, orient) in values])
    try:
        with conn.cursor() as cur:
            cur.execute(f"""UPDATE cropped_sign AS c 
                        SET gisement = new_values.gis, sdf = new_values.sdf, orientation = new_values.orient
                        FROM ( VALUES {values_sql}) AS new_values (id, sdf, gis, orient)
                        WHERE c.id = new_values.id;""")

            conn.commit()

            return detections
    except (Exception, DatabaseError) as error:
        raise error


def compute(detections):
    gisements = (detections.x / detections.source_width - 0.5) * detections.source_fov + detections.source_azimut
    detections["gisement"] = format_angle_deg(gisements)

    detections["sdf"] = detections.source_height / (detections.dz * 2 * pi)

    detections["orientation"] = 0 # TODO: complete this compute

if __name__ == "__main__":
    print("Connecting to database...\t\t\t", end="")
    conn, config = connect_db()
    print("Done")
    
    print("Loading uncomputed cropped_signs...\t\t", end="")
    detections = load(conn)
    print(f"Done : {len(detections)} cropped_signs")

    print("Computting gisement and sdf...\t\t\t", end="")
    compute(detections)
    print("Done")
    
    print("Saving...\t\t\t\t\t", end="")
    save(conn, detections)
    print("Done")
    
    print("Fin")
