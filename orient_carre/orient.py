from PIL import Image, ImageMath
import matplotlib.pyplot as plt
import numpy as np
from skimage import data, transform

detection = Image.open("./C28_detecte.jpg")

"""
print(detection.size)

img = Image.open("C28.png")

img2 = img.resize((16, 16))

img3 = img.resize((1,1))
r, g, b, _ = img3.getpixel((0,0))
print(img3.getpixel((0,0)))

red, green, blue = Image.Image.split(detection)

d2 = ImageMath.eval(f"255 - abs(red-{r}) - abs(green-{g}) - abs(blue-{b})", red=red, green=green, blue=blue)

db = ImageMath.eval(f"255 - abs(blue-{b})", blue=blue)
plt.imshow(db)
plt.show()

"""

def satureImage(img):
    hsv = img.convert("HSV")
    img2 = Image.new("HSV", hsv.size, (255, 255, 255))
    h, _, _ = Image.Image.split(hsv)
    _, s, v = Image.Image.split(img2)
    imgSat = Image.merge("HSV", (h, s, v))
    return imgSat.convert(img.mode)

"""
hsv = detection.convert("HSV").resize((1,1))
print(detection.mode)
print(hsv.getpixel((0,0)))
hsv.putpixel((0,0), (82, 255, 255))
"""

import os

def has_been_closed(ax):
    fig = ax.figure.canvas.manager
    active_fig_managers = plt._pylab_helpers.Gcf.figs.values()
    return fig not in active_fig_managers

def show_bands(directory):
    imgs_names = os.listdir(f"../DATA_BASE_SIMULEE/{directory}")

    fig = plt.figure()
    axs = fig.subplots(3, 4)
    [[ax_i, ax_h, ax_s, ax_v],
    [ax_l, ax_r, ax_g, ax_b],
    [ax_sat, _, _, _]] = axs
    axs = [ax for l in axs for ax in l]
    ax_i.set_title("image")
    ax_h.set_title("teinte")
    ax_s.set_title("saturation")
    ax_v.set_title("intensité")
    ax_r.set_title("rouge")
    ax_g.set_title("vert")
    ax_b.set_title("bleu")
    ax_l.set_title("gris")
    ax_sat.set_title("saturation2")
    for ax in axs:
        ax.axis("off")

    for name in imgs_names:
        img = Image.open(f"../DATA_BASE_SIMULEE/{directory}/{name}")
        h, s, v = Image.Image.split(img.convert("HSV"))
        r, g, b = Image.Image.split(img.convert("RGB"))
        if not has_been_closed(ax_i):
            fig.suptitle(f"../DATA_BASE_SIMULEE/{directory}/\n{name}")
            ax_i.imshow(img)
            ax_l.imshow(img.convert("L"), cmap="gray")
            ax_h.imshow(h, cmap="hsv")
            ax_s.imshow(s, cmap="gray")
            ax_v.imshow(v, cmap="gray")
            ax_r.imshow(r, cmap="Reds")
            ax_g.imshow(g, cmap="Greens")
            ax_b.imshow(b, cmap="Blues")
            ax_sat.imshow(satureImage(img))
            plt.waitforbuttonpress()

def rotateOrient(img, orient):
    tx = 0
    ty = 0

    S, C = np.sin(orient), np.cos(orient)

    # Rotation matrix, angle theta, translation tx, ty
    H = np.array([[C, -S, tx],
                [S,  C, ty],
                [0,  0, 1]])

    # Translation matrix to shift the image center to the origin
    r, c = img.size
    T = np.array([[1, 0, -c / 2.],
                [0, 1, -r / 2.],
                [0, 0, 1]])

    # Skew, for perspective
    S = np.array([[1, 0, 0],
                [0, 1.3, 0],
                [0, 1e-3, 1]])

    return transform.homography(img, S.dot(np.linalg.inv(T).dot(H).dot(T)))


lDir = ["A13a", "AB4", "AB6", "B14-50", "C28", "CE22", "../orient_carre/panneaux_officiels"]

if __name__ == "__main__":
    #show_bands(lDir[4])

    img = Image.open("panneaux_officiels/C28.png")

    imgR = rotateOrient(img, 0)

    plt.imshow(imgR)
    plt.show()