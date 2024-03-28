import pandas as pd
import numpy as np
from PIL import Image
import math
import pyproj
import matplotlib.pyplot as plt

print("""
Unités (sauf contre-indication):
    angles: radian
    distances: mètres
""")


"""
calculs des estimations:
    posSource
    dirSource
    fovSource
    widthSource

    gisement
    distance
    
"""


print("begin\n\n\n")

proj_geo_to_lambert = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:2154")
proj_lambert_to_geo = pyproj.Transformer.from_crs("EPSG:2154", "EPSG:4326")

# load data
dataset = "../data_test/cropped_signs"
photos = pd.read_csv(dataset + "/photo.csv")
imagettes = pd.read_csv(dataset + "/imagette.csv")

# add width and height
photos["width"] = 0
photos["height"] = 0

for key in photos.index:
    img = Image.open(dataset + "/photo/" + photos.loc[key].id + ".jpg")
    photos.loc[key, ("width", "height")] = (img.width, img.height)

# turn angle from deg to rad
photos["azimut_rad"] = photos.azimut * math.pi / 180
photos["fov_rad"] = photos.fov * math.pi / 180

# proj Lambert93

x, y = proj_geo_to_lambert.transform(photos.lat, photos.lng)
photos["x"] = x
photos["y"] = y

# join
imagettes = imagettes.join(photos.set_index("id").add_prefix("source_"), on="source")

# compute coords panneau

imagettes["gisement"] = ((imagettes.x / imagettes.source_width - 0.5) * imagettes.source_fov + imagettes.source_azimut) * math.pi / 180



# mc


"""
X = [
    pan1.x
    pan1.y
    pan1.size
    pan2.x
    ...
    panN.size
]

B = [
    de1.x
    de1.y
    de1.gisement
    de1.dz
    de2.x
    ...
    deN.dz
]

A contient les coorespondances entre detection et panneau
"""
