import pandas as pd

"""
TABLES

imagette: id, id_photo, id_panneau, x, y, dz, gisement, orientation, lat_estim, lng_estim, E_estim, N_estim, code
panneau: id, lat, lng, E, N, code, size, orientation
photo: id, azimut, fov, lat, lng, E, N, resol_x, resol_y, href
sequence: id, date

"""
def init():
    global imagette, panneau, photo, sequence
    imagette = pd.DataFrame()
    panneau = pd.DataFrame()
    photo = pd.DataFrame()
    sequence = pd.DataFrame()


def load():
    global imagette, panneau, photo, sequence
    
init()