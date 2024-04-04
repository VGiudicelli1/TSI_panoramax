import utils
import storage
from math import pi
from numpy import cos, sin

"""
Estime la position du panneau vu dans les imagettes d'une séquence
"""

def estim_img_pos_for_sequence(id_sequence):
    # load and proj data
    sequence, photo, imagette, panneau = storage.select_from_sequence(id_sequence)
    utils.proj_geo_to_lambert_delta(photo)

    # join
    imagette_photo = imagette.join(photo.set_index("id").add_prefix("source_"), on="id_photo")

    # compute gisement & size factor
    imagette_photo["gisement"] = ((imagette_photo.x / imagette_photo.source_width - 0.5) * imagette_photo.source_fov + imagette_photo.source_azimut) * pi / 180
    imagette_photo["size_dist_factor"] = imagette_photo.source_height / imagette_photo.dz / pi

    # estim new coordinates
    imagette["e"] = 0.8 * imagette_photo.size_dist_factor * sin(imagette_photo.gisement) + imagette_photo.source_e
    imagette["n"] = 0.8 * imagette_photo.size_dist_factor * cos(imagette_photo.gisement) + imagette_photo.source_n

    # unproj and save
    utils.proj_lambert_delta_to_geo(imagette)
    storage.update_imagette(imagette)


if __name__ == "__main__":
    from view_sequence import view_sequence
    id_sequence = storage.get_sequence_ids()[0]
    estim_img_pos_for_sequence(id_sequence)
    view_sequence(id_sequence)
