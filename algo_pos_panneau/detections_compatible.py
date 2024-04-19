from code_panneaux import is_code_back, is_code_face, get_code_back

import math, numpy as np

"""
detections requirements
code
value
sdf
gisement
orientation
source_id
source_E
source_N
"""

default_seuils = {
    "seuil_same_orientation_cos": 0.9, # => if orientation closest than 25° [ =acos(0.9) ], orientations are compatibles
    "seuil_dist_max_same_pos": 5
}

def are_source_compatible(detections, seuils=default_seuils):
    # test if all sources are differents (2 signs in a same picture are differents)
    values = list(detections.source_id.values)
    return len(values) == len(set(values))

def are_code_compatibles(detections, seuils=default_seuils):
    codes_face = {
        code 
        for code in detections.code.values 
        if is_code_face(code)
    }
    if len(codes_face) == 0:
        code_face = None
    elif len(codes_face) == 1:
        code_face = codes_face.pop()
    else:
        return False
    
    codes_back = {
        code 
        for code in detections.code.values 
        if is_code_back(code)
    }
    if len(codes_back) == 0:
        code_back = None
    elif len(codes_back) == 1:
        code_back = codes_back.pop()
    else:
        return False

    return (
        code_back == None 
        or code_face == None 
        or code_back == get_code_back(code_face)
    )

def are_values_compatibles(detections, seuils=default_seuils):
    values = {
        value 
        for code, value in detections.loc[:, ("code", "value")].values 
        if is_code_face(code)
    }
    return len(values) <= 1

def are_orientations_compatibles(detections, seuils=default_seuils):
    orientations = detections.orientation * math.pi / 180   # degrees to radian
    mean_angle = math.atan2(
        np.mean(np.sin(orientations)), 
        np.mean(np.cos(orientations))
    )
    cos = np.cos(orientations - mean_angle)
    criteria = np.min(cos)
    return criteria > default_seuils["seuil_same_orientation_cos"] # seuil 0.9 => tolerence 25° from mean angle by default

def are_positions_compatibles(detections, seuils=default_seuils):
    # MC : estimate position and size
    # criteria: max dist < 5m ?

    # x +0 -sdf_i*dx_i*size = x0_i
    # 0 +y -sdf_i*dy_i*size = y0_i

    # X = [[x],[y],[size]]
    # A = [[1,0,-sdf_i*dx_i],[0,1,-sdf_i*dy_i] for i]
    # B = [[x0_i], [y0_i] for i]

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

    B2 = A @ X - B

    E = B2[0::2, 0]
    N = B2[1::2, 0]

    dists = (E**2+N**2)**.5

    criteria = np.max(dists)

    return criteria < seuils["seuil_dist_max_same_pos"]

def are_detections_compatibles(detections, seuils=default_seuils):
    return (
        are_source_compatible(detections, seuils=seuils)
        and are_code_compatibles(detections, seuils=seuils)
        and are_values_compatibles(detections, seuils=seuils)
        #and are_orientations_compatibles(detections, seuils=seuils)
        and are_positions_compatibles(detections, seuils=seuils)
    )


def compatible_matrix(detections, seuils=default_seuils):
    # create compat_mat
    index = list(detections.index)
    n = len(index)
    revert_index = { index[k]:k for k in range(n) }

    compat_mat = np.eye(n, dtype=np.uint8)

    for i in range(n-1):
        for j in range(i+1, n):
            if are_detections_compatibles(
                detections.loc[detections.index.isin((index[i], index[j]))],
                seuils):
                compat_mat[i, j] = 1
                compat_mat[j, i] = 1

    return compat_mat, index, revert_index


if __name__ == "__main__":
    #from make_test_set import detections #, detections_noise

    #print(detections)
    #print(are_detections_compatibles(detections.loc[detections.index.isin([0, 3])]))

    #print(are_detections_compatibles(detections))
    pass