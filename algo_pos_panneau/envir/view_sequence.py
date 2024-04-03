import utils
import storage
import matplotlib.pyplot as plt
"""
Affiche les données de la séquence:
- photos,
- imagettes,
- panneaux
"""

id_sequence = storage.get_sequence_ids()[0]
sequence, photo, imagette, panneau = storage.select_from_sequence(id_sequence)

utils.proj_geo_to_lambert_delta(photo, delta=(0,0))
utils.proj_geo_to_lambert_delta(imagette, delta=(0,0))
utils.proj_geo_to_lambert_delta(panneau, delta=(0,0))

imagette_photo = imagette.join(photo.set_index("id").add_prefix("source_"), on="id_photo")

plt.axis("equal")
plt.title(f"Données de la séquence {id_sequence}\n(coordonnées Lambert)")
plt.plot(list(photo.e),    list(photo.n),    marker="o", lw=0, color="blue",   label=f"photo ({len(photo)})"      )
plt.plot(list(imagette.e), list(imagette.n), marker="x", lw=0, color="green",  label=f"imagette ({len(imagette)})")
plt.plot(list(panneau.e),  list(panneau.n),  marker="o", lw=0, color="orange", label=f"panneau ({len(panneau)})"  )

for i_img in imagette_photo.index:
    img = imagette_photo.loc[i_img]
    plt.plot([img.e, img.source_e], [img.n, img.source_n], lw=0.2, color="blue")
plt.legend()
plt.show()