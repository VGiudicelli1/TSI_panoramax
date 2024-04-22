from database_connect import connect_db, DatabaseError
import pandas as pd
from clusterise import clusterise_mat, extract_clusters
from detections_compatible import compatible_matrix, are_detections_compatibles
from utils import proj_geo_to_lambert_delta, proj_lambert_delta_to_geo, format_angle_deg
import numpy as np
import math
from code_panneaux import is_code_face

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


def save_new_panneaux(conn, panneaux):
    index = panneaux.id.isnull()
    try:
        with conn.cursor() as cur:
            proj_lambert_delta_to_geo(panneaux)
            values = ", ".join([
                f"(ST_POINT({e[0]},{e[1]}), {e[2]}, '{e[3]}', '{e[4]}', {e[5]}, -1)"
                for e in panneaux.loc[index, ("lng", "lat", "size", "code", "value", "orientation")].values
            ])
            cur.execute(f"""
                INSERT INTO sign (geom, size, code, value, orientation, precision)
                VALUES {values}
                RETURNING id
            """)
            panneaux.loc[index, "id"] = cur.fetchall()
            conn.commit()
    except (Exception, DatabaseError) as error:
        raise error

def save_detections(conn, detections):
    values = ", ".join([
        f"({id}, {p_id})"
        for (id, p_id) in detections.loc[:, ("id", "panneau_id")].values
    ])
    try:
        with conn.cursor() as cur:
            cur.execute(f"""UPDATE cropped_sign AS c 
                        SET sign_id = new_values.p_id
                        FROM ( VALUES {values}) AS new_values (id, p_id)
                        WHERE c.id = new_values.id;""")
            conn.commit()
    except (Exception, DatabaseError) as error:
        raise error

# clusterise
def clusterise(detections):
    compat_mat, _, rindex = compatible_matrix(detections)
    cluster_mat = clusterise_mat(compat_mat)
    clusters = extract_clusters(cluster_mat)

    cluster_reduct = [
        [ rindex[i] for i in cluster]
        for cluster in clusters if len(cluster)>=5
    ]
    return cluster_reduct


# extract panneau
def compute_panneau_unique(detections):
    # critere minimum:
    #  3 detections de face (code_face)
    
    panneau = pd.DataFrame(
        [[None, None, None, None, None, None, None]], 
        columns=("id", "e", "n", "size", "orientation", "code", "value")
    )

    # e, n, size: par moindre carrés
    n = len(detections)
    A = np.zeros((2*n, 3))
    B = np.zeros((2*n, 1))

    B[0::2, 0] = detections.source_E
    B[1::2, 0] = detections.source_N

    A[0::2, 0] = 1
    A[1::2, 1] = 1
    A[0::2, 2] = -detections.sdf * np.sin(detections.gisement * math.pi / 180)
    A[1::2, 2] = -detections.sdf * np.cos(detections.gisement * math.pi / 180)

    X = np.linalg.lstsq(A, B, rcond=None)[0]
    panneau.loc[0, ("e", "n", "size")] = X.reshape(3)

    # orientation: moyenne
    orientations = detections.orientation * math.pi / 180   # degrees to radian
    panneau.loc[0, "orientation"] = math.atan2(
        np.mean(np.sin(orientations)), 
        np.mean(np.cos(orientations))
    ) * 180 / math.pi

    # code, valeur: minimum 3 de face
    codes = [ (code, value) for (value, code) in detections.loc[:, ("value", "code")].values if is_code_face(code)]
    if len(codes) < 3:
        return
    panneau.loc[0, ("code", "value")] = codes[0]

    return panneau

def makeLetterId(nb):
    return (makeLetterId(nb//26) if nb//26 else "") + chr(ord('a')+(nb%26))

def compute_panneaux(detections, clusters):
    panneaux = pd.DataFrame(
        [], 
        columns=("id", "e", "n", "size", "orientation", "code", "value", "temp_id")
    )
    detections.loc[:, "panneau_id_temp"] = None

    for cluster in clusters:
        panneau = compute_panneau_unique(detections.loc[detections.index.isin(cluster)])
        if panneau is not None:
            i = len(panneaux)
            panneau_id = makeLetterId(i)
            panneau.loc[0, "temp_id"] = panneau_id
            panneaux.loc[i] = panneau.loc[0]
            detections.loc[detections.index.isin(cluster), "panneau_id_temp"] = panneau_id

    return panneaux


# appareille
def appareille_panneaux(panneaux_detectes, panneaux_connus):
    """
    lie les panneaux detectés aux panneaux connus
    Les panneaux detectés non liés devront etre ajouté à la base
    Le panneaux connus non liés : normal si on ne travaille pas sur toutes les detections
    """
    def dist(i, j):
        p1 = panneaux_detectes.loc[i]
        p2 = panneaux_connus.loc[j]
        dist_plani = ((p1.e - p2.e)**2 + (p1.n - p2.n)**2 ) **.5
        dist_size = abs(p1["size"] - p2["size"])
        dist_orient = abs(format_angle_deg(p1.orientation - p2.orientation))
        if p1.code != p2.code or p1.value != p2.value or dist_plani > 10 or dist_size > 0.5 or dist_orient > 90:
            return np.inf
        return dist_plani + 10*dist_size + dist_orient/10
    
    index1 = list(panneaux_detectes.index)
    index2 = list(panneaux_connus.index)
    links = appareille_list(index1, index2, dist)

    # update ids
    for (idx_p_d, idx_p_c) in links:
        panneaux_detectes.loc[idx_p_d, "id"] = panneaux_connus.loc[idx_p_c, "id"]
    
    return links

def appareille_list(l1, l2, dist):
    if len(l1) == 0 or len(l2) == 0:
        return []
    dists = np.array([[dist(e1, e2) 
                       for e1 in l1] 
                       for e2 in l2])
    min1 = np.argmin(dists, axis=0)
    min2 = np.argmin(dists, axis=1)

    return [(i, min1[i]) for i in range(len(min1)) if i == min2[min1[i]] and dists[min1[i], i] != np.inf]


def update_detection_fk_id(detections, panneaux):
    d2 = detections.join(panneaux.set_index("temp_id").add_prefix("p_"), on="panneau_id_temp")
    detections.loc[:, "panneau_id"] = d2.loc[:, "p_id"].replace({np.nan: None})

if __name__ == "__main__":
    print("Connecting to database...\t\t\t", end="")
    conn, config = connect_db()
    print(f"Done")
    
    print("Loading cropped_signs and signs...\t\t", end="")
    detections, panneaux = load(conn)  # les detections qui n'ont pas toutes les informations calculées (gisement, sdf, orientation) ne sont pas chargées
    print(f"Done : {len(detections)} cropped_signs; {len(panneaux)} signs")

    print("Clusterise...\t\t\t\t\t", end="")
    clusters = clusterise(detections)
    print(f"Done : {len(clusters)} clusters")

    print("Extract signs...\t\t\t\t", end="")
    panneaux_detectes = compute_panneaux(detections, clusters)
    print(f"Done : {len(panneaux_detectes)} panneaux detectés")

    print("Appareillage avec les panneaux connus...\t", end="")
    links = appareille_panneaux(panneaux_detectes, panneaux)
    print(f"Done : {len(links)} liens")

    print("Enregistrement des nouveaux panneaux...\t\t", end="")
    save_new_panneaux(conn, panneaux_detectes)
    print("UNDONE (TODO)")

    print("Mise à jour des detections...\t\t\t", end="")
    update_detection_fk_id(detections, panneaux_detectes)
    save_detections(conn, detections)
    print("UNDONE (TODO)")

    print("fin")