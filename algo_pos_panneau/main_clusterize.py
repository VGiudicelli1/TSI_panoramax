from database_connect import connect_db, DatabaseError
import pandas as pd
from clusterise import clusterise_mat, extract_clusters
from detections_compatible import compatible_matrix
from utils import proj_geo_to_lambert_delta, proj_lambert_delta_to_geo

## necessite que compute_cropped_measurement soit executé avant


# charger les detection
# charger les panneaux
# clusteriser les detections
# appareiller sur les panneaux existants: code/val egal, minimiser les distances (e, n, size, orientation)
# nouveaux panneaux pour les clusters de plus de 5 detections dont 3 de face

def load(conn):
    try:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT c.id, p.id, ST_X(p.geom), ST_Y(p.geom), c.code, c.value, c.orientation, c.gisement, c.sdf
	            FROM picture AS p 
	            JOIN cropped_sign AS c ON c.picture_id = p.id
                WHERE c.code IS NOT NULL 
                    AND c.orientation IS NOT NULL 
                    AND c.gisement IS NOT NULL 
                    AND c.sdf IS NOT NULL 
                """)
            detections = pd.DataFrame(
                cur.fetchall(), 
                columns=("id", "source_id", "source_lng", "source_lat", "code", "value", "orientation", "gisement", "sdf")
                )
            proj_geo_to_lambert_delta(detections, "source_lat", "source_lng", "source_E", "source_N")
    
            cur.execute(f"""
                SELECT id, ST_X(geom), ST_Y(geom), size, orientation, code, value
	            FROM sign
                """)
            panneaux = pd.DataFrame(
                cur.fetchall(), 
                columns=("id", "lng", "lat", "size", "orientation", "code", "value")
                )
            proj_geo_to_lambert_delta(panneaux)

            conn.commit()

            return detections, panneaux
    except (Exception, DatabaseError) as error:
        raise error

# clusterise

def clusterise(detections):
    compat_mat, index, rindex = compatible_matrix(detections)
    print(compat_mat)
    cluster_mat = clusterise_mat(compat_mat)
    clusters = extract_clusters(cluster_mat)
    
    detections.loc[:, "cluster"] = None

    for i_cluster, cluster in zip(range(len(clusters)), clusters):
        for i in cluster:
            detections.loc[rindex[i], "cluster"] = i_cluster

    print(detections)

# appareille

# 

if __name__ == "__main__":
    print("Connecting to database...\t\t", end="")
    conn, config = connect_db()
    print("Done")
    
    print("Loading cropped_signs and signs...\t", end="")
    detections, panneaux = load(conn)  # les detections qui n'ont pas toutes les informations calculées (gisement, sdf, orientation) ne sont pas chargées
    print(f"Done : {len(detections)} cropped_signs; {len(panneaux)} signs")

    print(detections)
    print(panneaux)

    print("clusterise")
    clusterise(detections)

    print("fin")