"""
Fonctions utilitaires diverses
"""
from pyproj import Transformer as _Transformer
from numpy import mean as _mean
import numpy as np

###############################################################################
##  Projection                                                               ##
###############################################################################

_transformer_geo_to_lambert = _Transformer.from_crs("EPSG:4326", "EPSG:2154")
_transformer_lambert_to_geo = _Transformer.from_crs("EPSG:2154", "EPSG:4326")

_DELTA = None

def proj_geo_to_lambert_delta(df, lat_column="lat", lng_column="lng", e_column="e", n_column="n", delta=None):
    """
    if delta == None: delta = (mean(e), mean(n))
    return delta
    """
    global _DELTA
    E, N = _transformer_geo_to_lambert.transform(df.loc[:, (lat_column, )], df.loc[:, (lng_column, )])
    if delta==None:
        if _DELTA==None:
            delta = (_mean(E), _mean(N))
            _DELTA = delta
        else:
            delta = _DELTA
    df.loc[:, (e_column, )] = E - delta[0]
    df.loc[:, (n_column, )] = N - delta[1]

    return delta

def proj_lambert_delta_to_geo(df, lat_column="lat", lng_column="lng", e_column="e", n_column="n", delta=None):
    """
    if delta == None: delta = last auto delta apply or raise
    """
    if delta == None:
        delta = _DELTA
        if delta == None:
            raise Exception("no delta found")

    lat, lng = _transformer_lambert_to_geo.transform(df.loc[:, (e_column, )] + delta[0], df.loc[:, (n_column, )] + delta[1])
    df.loc[:, (lat_column, )] = lat
    df.loc[:, (lng_column, )] = lng

###############################################################################
##  Clusterisation                                                           ##
###############################################################################

def kmean(pts, k, max_itter = 100):
    if k>len(pts):
        raise ValueError("Too many classes. Need k <= len(pts)")
    centroides = np.array(pts[:k], dtype = np.float64)
    classif = np.zeros(len(pts))-1
    
    for _ in range(max_itter):
        dists = np.array([np.linalg.norm(pts - centroides[i], axis=1) for i in range(k)])

        prev_classif = classif
        classif = np.argmin(dists, axis=0)

        for i in range(k):
            pts_class = pts[classif == i]
            if (len(pts_class)==0):
                centroides[i]+=0.1 # si aucun point dans le cluster, on décale un peu le centroïde (ce cas peut arriver si deux centroides sont identiques au départ)
            else:
                centroides[i] = np.mean(pts_class, axis=0)

        # test sur la classif et non sur les centroides (cas particulier lorsque tous les points sont identiques)
        if not (prev_classif-classif).any():
            break

    dMoy = np.zeros(k)
    for i in range(k):
        pts_class = pts[classif == i]
        if (len(pts_class)!=0):
            dMoy[i] = np.mean(np.linalg.norm(pts_class - centroides[i], axis=1))
            
    return classif, centroides, dMoy

if __name__ == "__main__":
    ###########################################################################
    ##  Test unitaires                                                       ##
    ###########################################################################
    import pandas as pd

    data = pd.DataFrame([
        ["Paris", 48.866, 2.333], 
        ["Lyon", 45.750, 4.850], 
        ["Toulouse", 43.600, 1.433]
    ], columns=("ville", "lat", "lng"))
    proj_geo_to_lambert_delta(data, delta=[0,0])
    #print(data)
    assert abs(data.loc[0].e-651069.12) + abs(data.loc[0].n-6863092.19) < 1

    data.lat = 0
    data.lng = 0
    proj_lambert_delta_to_geo(data, delta=[0,0])
    #print(data)
    assert abs(data.loc[0].lat-48.866) + abs(data.loc[0].lng-2.333) < 0.01


    pts = np.array([
        [0, 1],
        [1, 1],
        [0, 1],
        [9, 1],
        [8, 1]
    ])
    print(kmean(pts, 2))