import pandas as pd
import numpy as np
from PIL import Image
import math
import pyproj
import matplotlib.pyplot as plt

__path__ = "/".join(__file__.split("/")[:-1])

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

print("load data...")
# load data
dataset = __path__ + "/../data_test/cropped_signs"
photos = pd.read_csv(dataset + "/photo.csv")
imagettes = pd.read_csv(dataset + "/imagette.csv")

# add width and height
photos["width"] = 0
photos["height"] = 0

for key in photos.index:
    img = Image.open(dataset + "/photo/" + photos.loc[key].id + ".jpg")
    photos.loc[key, ("width", "height")] = (img.width, img.height)

print("init data...")
# turn angle from deg to rad
photos["azimut_rad"] = photos.azimut * math.pi / 180
photos["fov_rad"] = photos.fov * math.pi / 180

# proj Lambert93
E, N = proj_geo_to_lambert.transform(photos.lat, photos.lng)
DELTA_E = np.mean(E)
DELTA_N = np.mean(N)
photos["E"] = E - DELTA_E
photos["N"] = N - DELTA_N

# join
imagettes = imagettes.join(photos.set_index("id").add_prefix("source_"), on="source")

# compute angle hauteur dz_rad
imagettes["size_dist_factor"] = imagettes.source_height / imagettes.dz / math.pi
# dist = size_dist_factor * size

# compute gisement
imagettes["gisement"] = ((imagettes.x / imagettes.source_width - 0.5) * imagettes.source_fov + imagettes.source_azimut) * math.pi / 180

print("compute position...")
# propag
imagettes["E_estim"] = 0.8 * imagettes.size_dist_factor * np.sin(imagettes.gisement) + imagettes.source_E
imagettes["N_estim"] = 0.8 * imagettes.size_dist_factor * np.cos(imagettes.gisement) + imagettes.source_N

# MC with appareillment of panneaux
"""
1-2-7-9
3-4
5-6-8-10
"""
"""
B = Es, Ns, gisement, size_dist_factor
X = Ep,Np,s
"""

appareillement = [
    [0,1,6,8],
    [4,5,7,9],
    [2, 3]
]
nb_pan = len(appareillement)
nb_img = len(imagettes)

B = np.zeros((nb_img * 4,1))
B[0::4, 0] = imagettes.source_E
B[1::4, 0] = imagettes.source_N
B[2::4, 0] = imagettes.gisement
B[3::4, 0] = imagettes.size_dist_factor
#print(B)

X = np.zeros((nb_pan * 3, 1))
X[0::3, 0] = 0  # pos E
X[1::3, 0] = 0  # pos N
X[2::3, 0] = 1  # taille du panneau en mètres
for i in range(len(appareillement)):
    X[3*i  , 0] = np.mean(imagettes.loc[appareillement[i]].E_estim)
    X[3*i+1, 0] = np.mean(imagettes.loc[appareillement[i]].N_estim)
#print(X)

def makedA():
    dA = np.zeros((nb_img*4, nb_pan*3))
    for i_pan in range(len(appareillement)):
        for i_img in appareillement[i_pan]:

            x = imagettes.loc[i_img].source_E - X[i_pan*3+0]
            y = imagettes.loc[i_img].source_N - X[i_pan*3+1]
            dist2 = x**2+y**2
            dist = dist2**.5
            fds = imagettes.loc[i_img].size_dist_factor
            gisement = imagettes.loc[i_img].gisement
            size = X[i_pan*3+2]

            dA[4*i_img+0, 3*i_pan+0] = 1                            # d sourceE / d posE
            dA[4*i_img+0, 3*i_pan+1] = 0                            # d sourceE / d posN
            dA[4*i_img+0, 3*i_pan+2] = -fds * math.sin(gisement)    # d sourceE / d size

            dA[4*i_img+1, 3*i_pan+0] = 0                            # d sourceN / d posE
            dA[4*i_img+1, 3*i_pan+1] = 1                            # d sourceN / d posN
            dA[4*i_img+1, 3*i_pan+2] = -fds * math.cos(gisement)    # d sourceN / d size

            dA[4*i_img+2, 3*i_pan+0] = -y/dist2                     # d gisement / d posE
            dA[4*i_img+2, 3*i_pan+1] = x/dist2                      # d gisement / d posN
            dA[4*i_img+2, 3*i_pan+2] = 0                            # d gisement / d size

            dA[4*i_img+3, 3*i_pan+0] = 1 / size / math.sin(gisement)# d size_dist_factor / d posE
            dA[4*i_img+3, 3*i_pan+1] = 1 / size / math.cos(gisement)# d size_dist_factor / d posN
            dA[4*i_img+3, 3*i_pan+2] = 1 / dist                     # d size_dist_factor / d size
    return dA

def makeBact():
    B = np.zeros((nb_img*4, 1))
    for i_pan in range(len(appareillement)):
        for i_img in appareillement[i_pan]:
            x = X[i_pan*3+0] - imagettes.loc[i_img].source_E
            y = X[i_pan*3+1] - imagettes.loc[i_img].source_N
            dist2 = x**2+y**2
            dist = dist2**.5
            fsd = imagettes.loc[i_img].size_dist_factor
            gisement_act = math.atan2(y, x)
            size = X[i_pan*3+2]
            gisement_mes = imagettes.loc[i_img].gisement


            B[4*i_img+0, 0] = X[i_pan*3+0] - size * fsd * math.sin(gisement_mes)
            B[4*i_img+1, 0] = X[i_pan*3+1] - size * fsd * math.cos(gisement_mes)
            B[4*i_img+2, 0] = gisement_act
            B[4*i_img+3, 0] = dist / size
            
    return B

for i in range(100):
    dA = makedA()
    
    dB = makeBact() - B

    dX = np.linalg.lstsq(dA, dB , rcond=None)[0]

    norm_dX = np.linalg.norm(dX)
    norm_dB = np.linalg.norm(dB)

    #print(f"norm dB {norm_dB}\tnorm dX {norm_dX}")

    X -= dX

    if norm_dX < 1e-10:
        print(f"converge: {i}")
        print(dB)
        print(norm_dB)
        break

print(np.linalg.norm(dB[0::4])/nb_img)
print(np.linalg.norm(dB[1::4])/nb_img)
print(np.linalg.norm(dB[2::4])/nb_img)
print(np.linalg.norm(dB[3::4])/nb_img)

imagettes["E_reel"] = 0
imagettes["N_reel"] = 0


panneaux = { i: {"imagettes":list(imagettes.loc[appareillement[i]].source)} for i in range(len(appareillement)) }

for i_pan in range(len(appareillement)):
    for i_img in appareillement[i_pan]:
        imagettes.loc[i_img, ("E_reel", "N_reel")] = (X[3*i_pan+0, 0], X[3*i_pan+1, 0])
        panneaux[i_pan]["coords"] = {"E": X[3*i_pan+0, 0] + DELTA_E, "N": X[3*i_pan+1, 0] + DELTA_N}

# unproj Lambert93

lat, lng = proj_lambert_to_geo.transform(imagettes.E_reel, imagettes.N_reel)
imagettes["lat_reel"] = lat
imagettes["lng_reel"] = lng

print("display...")
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
    plt.plot(photo.E, photo.N, marker=makeMarkerPhoto(photo.azimut_rad, photo.fov_rad), markersize=50)
    plt.text(photo.E, photo.N, str(photo.id)[:5]+"...")

def display_img(imgs):
    print(imgs)
    plt.plot(
        list(zip(*zip(imgs.E_reel, imgs.source_E))),
        list(zip(*zip(imgs.N_reel, imgs.source_N))),
        marker="x", lw=1)

    for key in imgs.index:
        img = imgs.loc[key]
        #plt.plot([img.x_reel, img.source_x], [img.y_reel, img.source_y], marker="x")
        plt.text(img.E_reel, img.N_reel, str(img.code))


#display_img(imagettes[imagettes.code == "B14"])
display_img(imagettes)
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
