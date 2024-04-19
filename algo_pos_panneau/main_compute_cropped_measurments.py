from database_connect import connect_db, DatabaseError
import pandas as pd
from math import pi
import numpy as np
from utils import format_angle_degrees
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
    values = data.loc[:, ("id", "sdf", "gisement")].values
    values_sql = ", ".join([f"({id}, {sdf}, {gis})" for id, sdf, gis in values])
    try:
        with conn.cursor() as cur:
            cur.execute(f"""UPDATE cropped_sign AS c 
                        SET gisement = new_values.gis, sdf = new_values.sdf
                        FROM ( VALUES {values_sql}) AS new_values (id, sdf, gis)
                        WHERE c.id = new_values.id;""")

            conn.commit()

            return detections
    except (Exception, DatabaseError) as error:
        raise error


def compute(detections):
    gisements = (detections.x / detections.source_width - 0.5) * detections.source_fov + detections.source_azimut
    detections["gisement"] = format_angle_degrees(gisements)

    detections["sdf"] = detections.source_height / (detections.dz * 2 * pi)

if __name__ == "__main__":
    print("Connecting to database...\t\t", end="")
    conn, config = connect_db()
    print("Done")
    
    print("Loading uncomputed cropped_signs...\t", end="")
    detections = load(conn)
    print(f"Done : {len(detections)} cropped_signs")

    print("Computting gisement and sdf...\t\t", end="")
    compute(detections)
    print("Done")
    
    print("Saving...\t\t\t\t", end="")
    save(conn, detections)
    print("Done")
    
    print("End")