import utils
import storage
import numpy as np

"""
appareille les détections de panneaux entre eux, en se basant sur les critères
suivants:
- position (proche)
- code (compatible)
- valeur (compatible selon le code)
- orientation (proche à 2pi près)

Différencie selon les critères suivants:
- photo identique
"""

"""
dans un premier temps, on utilise les critères suivants:
- position proche
- code égal
- valeur égale
"""

def appareil_pan_with_estim_pos(id_sequence):
    # load and proj data
    sequence, photo, imagette, panneau = storage.select_from_sequence(id_sequence)
    utils.proj_geo_to_lambert_delta(imagette)
    utils.proj_geo_to_lambert_delta(panneau)

    # appareil
    panneau_extraits = panneau.loc[()].copy()

    # separe with code and value
    imagette["cluster_CV"] = -1
    nb_clusters = 0
    for cluster_act in range(len(imagette)):
        index = imagette.loc[imagette.cluster_CV == -1].index
        if not len(index):
            nb_clusters = cluster_act
            break
        same_code = imagette.code==imagette.loc[index[0]].code
        value = imagette.loc[index[0]].value
        same_value = imagette.value==value if value != None else imagette.value.isnull()
        imagette.loc[same_code * same_value, ("cluster_CV", )] = cluster_act

    new_panneaux = []

    for cluster_nb in range(nb_clusters):
        cluster = imagette.loc[imagette.cluster_CV == cluster_nb]
        #print(cluster)
        pts = np.array(cluster.loc[:, ("e", "n")])

        for k in range(len(pts)):
            classif, centroides, dMoy = utils.kmean(pts, k+1)
            if np.max(dMoy) < 10:
                break

        for i in range(k+1):
            new_panneaux.append((list(cluster.index[classif==i]), centroides[i]))

    for ids_img, pos in new_panneaux:
        i = len(panneau)
        id = storage.get_new_unique_id_panneau()
        panneau.loc[i] = None #(None, None, None, None, None, imagette.loc[ids_img[0]].code, imagette.loc[ids_img[0]].value, pos[0], pos[1])
        panneau.loc[i, ("size", "orientation", "precision")] = 0
        panneau.loc[i, ("id", "code", "value", "e", "n")] = (id, imagette.loc[ids_img[0]].code, imagette.loc[ids_img[0]].value, pos[0], pos[1])
        imagette.loc[ids_img, ("id_panneau", )] = id


    # unproj and save
    utils.proj_lambert_delta_to_geo(panneau)
    utils.proj_lambert_delta_to_geo(imagette)

    storage.update_panneau(panneau)
    storage.update_imagette(imagette)


if __name__ == "__main__":
    from view_sequence import view_sequence
    id_sequence = storage.get_sequence_ids()[0]
    appareil_pan_with_estim_pos(id_sequence)
    view_sequence(id_sequence)
