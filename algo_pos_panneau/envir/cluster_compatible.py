from v2_compatible import are_detections_compatibles
from make_test_set import detections_noise as detections

import numpy as np
import matplotlib.pyplot as plt

print(detections)

index = list(detections.index)
n = len(index)

compat_mat = np.eye(n, dtype=np.uint8)

for i in range(n-1):
    for j in range(i+1, n):
        if (are_detections_compatibles(detections.loc[detections.index.isin((index[i], index[j]))])):
            compat_mat[i, j] = 1
            compat_mat[j, i] = 1

print(compat_mat)

fig = plt.figure()

ax1, ax2 = fig.subplots(1, 2)

def has_been_closed(ax):
    fig = ax.figure.canvas.manager
    active_fig_managers = plt._pylab_helpers.Gcf.figs.values()
    return fig not in active_fig_managers

nb_liss = 20
for k in range(nb_liss):
    ax1.set_title(f"compat {k+1}/{nb_liss}")
    ax2.set_title(f"mat {k+1}/{nb_liss}")
    mat2 = np.eye(n)

    for i in range(n):
        for j in range(n):
            if compat_mat[i, j]:
                mat2[i, j] = np.sum(compat_mat[i, :] & compat_mat[j, :]) / np.sum(compat_mat[i, :] | compat_mat[j, :])
    print(mat2)
    print(compat_mat)

    if not has_been_closed(ax1):
        ax1.matshow(compat_mat)
        ax2.matshow(mat2)
        plt.waitforbuttonpress()

    compat_mat *= mat2 >= 0.9*(k+1)/nb_liss


clusters_keys = set(np.argmax(compat_mat, axis=1).tolist())

clusters = [
    np.argwhere(compat_mat[key]==1).T.tolist()[0]
    for key in clusters_keys
]

print(clusters)