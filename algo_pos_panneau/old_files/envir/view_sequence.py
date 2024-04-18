import utils
import storage
import matplotlib.pyplot as plt
import numpy as np
"""
Affiche les données de la séquence:
- photos,
- imagettes,
- panneaux
"""

def view_sequence(id_sequence):
    sequence, photo, imagette, panneau = storage.select_from_sequence(id_sequence)

    utils.proj_geo_to_lambert_delta(photo, delta=(0,0))
    utils.proj_geo_to_lambert_delta(imagette, delta=(0,0))
    utils.proj_geo_to_lambert_delta(panneau, delta=(0,0))

    imagette_photo_panneau = imagette.join(photo.set_index("id").add_prefix("source_"), on="id_photo").join(panneau.set_index("id").add_prefix("dest_"), on="id_panneau")

    plt.axis("equal")
    plt.title(f"Données de la séquence {id_sequence}\n(coordonnées Lambert)")
    plt.plot(list(photo.e),    list(photo.n),    marker="o", lw=0, color="blue",   label=f"photo ({len(photo)})"      )
    plt.plot(list(imagette.e), list(imagette.n), marker="x", lw=0, color="green",  label=f"imagette ({len(imagette)})")
    plt.plot(list(panneau.e),  list(panneau.n),  marker="o", lw=0, color="orange", label=f"panneau ({len(panneau)})"  )

    X = np.zeros((3 * len(imagette_photo_panneau), ))
    X[0::3] = imagette_photo_panneau.e
    X[2::3] = None

    Y = np.zeros((3 * len(imagette_photo_panneau), ))
    Y[0::3] = imagette_photo_panneau.n
    Y[2::3] = None

    X[1::3] = imagette_photo_panneau.source_e
    Y[1::3] = imagette_photo_panneau.source_n
    plt.plot(X, Y, lw=0.2, color="blue")

    X[1::3] = imagette_photo_panneau.dest_e
    Y[1::3] = imagette_photo_panneau.dest_n
    plt.plot(X, Y, lw=0.2, color="orange")

    plt.legend()
    plt.show()

if __name__ == "__main__":
    id_sequence = storage.get_sequence_ids()[0]
    view_sequence(id_sequence)
