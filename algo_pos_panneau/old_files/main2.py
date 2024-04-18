import pandas as pd
#import numpy as np
from PIL import Image
import math
import pyproj

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
    gisement
    distance
    
"""


print("begin\n\n\n")

proj_geo_to_lamert = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:2154")
proj_lamert_to_geo = pyproj.Transformer.from_crs("EPSG:2154", "EPSG:4326")

dataset = "./data_test/cropped_signs"
photos = pd.read_csv(dataset + "/photo.csv")
imagettes = pd.read_csv(dataset + "/imagette.csv")

def loadImage(id):
    return Image.open(dataset + "/photo/" + id + ".jpg")

def analyse(ln):
    img = loadImage(ln.source)
    source = photos.loc[photos.id == ln.source].iloc[0]
    gisement = (ln.x/img.width-0.5) * source.fov + source.azimut
    
    posSource = {
        "lat": source.lat,
        "lng": source.lng,
    }

    return {
        "id": ln.id,
        "source": source.id,
        "gisement": gisement * math.pi / 180,
        "posSource": {
            "lat": source.lat,
            "lng": source.lng,
        },
        "distanceMax": 50,
        "code": ln.code,
    }

def makeLineStringFromAnalyse(result):
    lat = result["posSource"]["lat"]
    lng = result["posSource"]["lng"]
    x, y = proj_geo_to_lamert.transform(lat, lng)
    x2, y2 = makePtFromGisementLambert(x, y, result["gisement"], result["distanceMax"])
    lat2, lng2 = proj_lamert_to_geo.transform(x2, y2)
    return makeLineString(lng, lat, lng2, lat2)

def makeLineString(x1, y1, x2, y2):
    return f"LineString ({x1} {y1}, {x2} {y2})"

def makePtFromGisementLambert(x, y, gisement, distance):
    return x + distance * math.cos(gisement), y + distance * math.sin(gisement)
    
#result = analyse(imagettes.loc[1])
#print(result)
#print(makeLineStringFromAnalyse(result))

def makeQueryInsert(line):
    result = analyse(imagettes.loc[line])
    lineString = makeLineStringFromAnalyse(result)
    id = result["id"]
    source = result["source"]
    code = result["code"]
    return f"INSERT INTO panneau_detection (id, source, code, geom) VALUES ('{id}', '{source}', '{code}', ST_GeomFromText('{lineString}'));"

"""
print(makeQueryInsert(2))
print(makeQueryInsert(3))
print(makeQueryInsert(4))
print(makeQueryInsert(5))
"""

print("\n\n\nend\n\n\n")