"""
Fonctions utilitaires diverses
"""
from pyproj import Transformer as _Transformer
from numpy import mean as _mean

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
    print(data)
    assert abs(data.loc[0].e-651069.12) + abs(data.loc[0].n-6863092.19) < 1

    data.lat = 0
    data.lng = 0
    proj_lambert_delta_to_geo(data, delta=[0,0])
    print(data)
    assert abs(data.loc[0].lat-48.866) + abs(data.loc[0].lng-2.333) < 0.01
