import numpy as np

def compute_mat_sim(mat):
    n = mat.shape[0]
    mat_sim = np.eye(n)
    for i in range(n):
        for j in range(n):
            if mat[i, j]:
                mat_sim[i, j] = np.sum(mat[i, :] & mat[j, :]) / np.sum(mat[i, :] | mat[j, :])
    return mat_sim

def clusterise_mat(compat_mat, steps=10, displayer=None):
    n = compat_mat.shape[0]
    for step in range(steps):
        mat_sim = compute_mat_sim(compat_mat)

    if displayer:
        displayer(compat_mat, mat_sim, step, steps)
        # displaying
        """
        if not has_been_closed(ax1):
            ax1.matshow(compat_mat)
            ax2.matshow(mat2)
            plt.waitforbuttonpress()
        """

        # seuil & reassign
        compat_mat *= mat_sim >= (step+1)/steps
    return compat_mat

def extract_clusters(clusterised_mat):
    clusters_keys = set(np.argmax(clusterised_mat, axis=1).tolist())

    clusters = [
        np.argwhere(clusterised_mat[key]==1).T.tolist()[0]
        for key in clusters_keys
    ]
    return clusters




if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from detections_compatible import compatible_matrix
    import pandas as pd

    fig = plt.figure()
    ax1, ax2 = fig.subplots(1, 2)
    def has_been_closed(ax):
        fig = ax.figure.canvas.manager
        active_fig_managers = plt._pylab_helpers.Gcf.figs.values()
        return fig not in active_fig_managers

    def displayer(compat_mat, mat_sim, step, steps):
        print(compat_mat)
        print(mat_sim)
        if not has_been_closed(ax1):
            ax1.set_title(f"compat {step+1}/{steps}")
            ax2.set_title(f"simil {step+1}/{steps}")
            ax1.matshow(compat_mat)
            ax2.matshow(mat_sim)
            plt.waitforbuttonpress()

    def make_dataset(noise = 0):
        data = pd.DataFrame([
            ["000",  0, 40, "B14", "30", -30.0,  116.565051, 11.180340],
            ["001", 40, 40, "A00", None, -30.0,  -99.462322, 30.413813],
            ["002", 45, 25, "A00", None, -30.0,  -74.054604, 36.400549],
            ["003", 20,  0, "A00", None, -30.0,  -15.945396, 36.400549],
            ["001", 40, 40, "B14", "30",  40.0, -126.869898,  8.333333],
            ["002", 45, 25, "B14", "30",  40.0,  -90.000000,  8.333333],
            ["003", 20,  0, "A00", None,  40.0,    0.000000,  8.333333],
            ["000",  0, 40, "A00", None, 160.0,  168.690068, 12.747549],
            ["001", 40, 40, "A00", None, 160.0, -125.537678, 21.505813],
            ["002", 45, 25,  "B1", None, 160.0, -104.036243, 20.615528],
            ["003", 20,  0,  "B1", None, 160.0,  -45.000000, 10.606602],
        ], columns=("source_id", "source_E", "source_N", "code", "value", "orientation", "gisement", "sdf"))

        size = len(data)
        data.source_E    += np.random.normal(loc=0, scale=0.5*noise, size=size)
        data.source_N    += np.random.normal(loc=0, scale=0.5*noise, size=size)
        data.orientation += np.random.normal(loc=0, scale=0.2*noise, size=size)
        data.gisement    += np.random.normal(loc=0, scale=0.2*noise, size=size)
        data.sdf         *= np.random.normal(loc=1, scale=0.1*noise, size=size)

        return data

    detections = make_dataset(0)

    print(detections)

    compat_mat, index, rindex = compatible_matrix(detections)
    print(compat_mat)

    # execute clusterisation
    clusterised_mat = clusterise_mat(compat_mat, displayer=displayer)

    # extract clusters
    clusters = extract_clusters(clusterised_mat)

    print(clusters)