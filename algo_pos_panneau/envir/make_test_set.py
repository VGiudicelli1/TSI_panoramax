import pandas as pd
import math
import numpy as np

from code_panneaux import is_code_back, is_code_face, get_code_back

scale = 5
# build jeu de test
ph = pd.DataFrame([
    ["000", 0, 8],
    ["001", 8, 8],
    ["002", 9, 5],
    ["003", 4, 0],
], columns=["id", "E", "N"])

pn = pd.DataFrame([
    [2, 7, -30, "B14", "30", 1],
    [4, 5,  40, "B14", "30", 3],
    [1, 3, 160, "B1" , None, 2]
], columns=["E", "N", "orientation", "code", "value", "size"])

# convert angles into radian
pn.orientation *= math.pi / 180

# scaling
ph.E *= scale
ph.N *= scale
pn.E *= scale
pn.N *= scale


detections = pd.DataFrame([
    [sId, sE, sN, c, get_code_back(c), v, o, math.atan2(pE-sE, pN-sN), ((pE-sE)**2+(pN-sN)**2)**.5/s]
    for (pE, pN, c, v, o, s) in pn.loc[:, ("E", "N", "code", "value", "orientation", "size")].values
    for (sId, sE, sN) in ph.loc[:, ("id", "E", "N")].values
], columns=["source_id", "source_E", "source_N", "code", "code_back", "value", "orientation", "gisement", "sdf"] )

cos_ang = np.cos(detections.orientation - detections.gisement)

detections.loc[cos_ang>0, "code"] = detections.loc[cos_ang>0, "code_back"]
detections.loc[cos_ang>0, "value"] = None
detections = detections.loc[abs(cos_ang) > 0.1].drop("code_back", axis=1)

#print(detections)

detections_noise = detections.copy()
# ajout de bruit
size = len(detections)
scale = 0
detections_noise.source_E    += np.random.normal(loc=0, scale=0.1*scale, size=size)
detections_noise.source_N    += np.random.normal(loc=0, scale=0.1*scale, size=size)
detections_noise.orientation += np.random.normal(loc=0, scale=0.2*scale, size=size)
detections_noise.gisement    += np.random.normal(loc=0, scale=0.2*scale, size=size)
detections_noise.sdf         *= np.random.normal(loc=1, scale=0.1*scale, size=size)

#print(detections)
