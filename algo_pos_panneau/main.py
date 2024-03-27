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
imagettes["x_reel"] = 50 * np.cos(imagettes.gisement) + imagettes.source_x
imagettes["y_reel"] = 50 * np.sin(imagettes.gisement) + imagettes.source_y

# unproj Lambert93

lat, lng = proj_lambert_to_geo.transform(imagettes.x_reel, imagettes.y_reel)
imagettes["lat_reel"] = lat
imagettes["lng_reel"] = lng

# view

def makeMarkerPhoto(azimut=0, fov=math.pi/2):
    pts = [(1,-0.5), (0,0), (-1,-0.5), (0,4)]
    pts = [(0, 2), (-1, 3), (0, 6), (1, 3), (0, 2),
           (2*math.sin(1*fov/8), 2*math.cos(1*fov/8)),
           (2*math.sin(2*fov/8), 2*math.cos(2*fov/8)),
           (2*math.sin(3*fov/8), 2*math.cos(3*fov/8)),
           (2*math.sin(4*fov/8), 2*math.cos(4*fov/8)),
           (0, 0),
           (-2*math.sin(4*fov/8), 2*math.cos(4*fov/8)),
           (-2*math.sin(3*fov/8), 2*math.cos(3*fov/8)),
           (-2*math.sin(2*fov/8), 2*math.cos(2*fov/8)),
           (-2*math.sin(1*fov/8), 2*math.cos(1*fov/8)),
           ]
    c = math.cos(azimut)
    s = math.sin(azimut)
    return [(x*c+y*s,y*c-x*s) for (x,y) in pts]

for key in photos.index:
    photo = photos.loc[key]
    plt.plot(photo.x, photo.y, marker=makeMarkerPhoto(photo.azimut_rad, photo.fov_rad), markersize=50)
    plt.text(photo.x, photo.y, str(photo.id)[:5]+"...")


print(imagettes)
plt.plot(
    list(zip(*zip(imagettes.x_reel, imagettes.source_x))),
    list(zip(*zip(imagettes.y_reel, imagettes.source_y))),
    marker="x", lw=1)

plt.axis("equal")
plt.show()

"""
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


"""
print(makeQueryInsert(2))
print(makeQueryInsert(3))
print(makeQueryInsert(4))
print(makeQueryInsert(5))
"""

print("\n\n\nend\n\n\n")
