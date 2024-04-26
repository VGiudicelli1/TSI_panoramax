from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import math

def transform_image(
        img:Image.Image, 
        new_size:tuple[int, int], 
        pts_ref_out:list[tuple[float, float]], 
        pts_ref_in:list[tuple[float, float]]
        ) -> Image.Image:

    pts_ref_in  = np.array(pts_ref_in )
    pts_ref_out = np.array(pts_ref_out)
    n = len(pts_ref_in)

    A = np.zeros((2*n, 8))
    A[0::2, 0:2] = pts_ref_out
    A[1::2, 3:5] = pts_ref_out
    A[0::2, 6:8] = - pts_ref_out * pts_ref_in[:, 0:1]
    A[1::2, 6:8] = - pts_ref_out * pts_ref_in[:, 1:2]
    A[0::2, 2] = 1
    A[1::2, 5] = 1
    
    B = np.zeros((2*n, 1))
    B[0::2, 0] = pts_ref_in[:, 0]
    B[1::2, 0] = pts_ref_in[:, 1]

    params = np.linalg.lstsq(A, B, rcond=None)[0][:, 0]
    return img.transform(new_size, Image.PERSPECTIVE, params, Image.BICUBIC)

def rot_3D(img:Image.Image, angle:float):
    w, h = img.size
    # build pts
    pts = np.array([[0.0, 0, 0], [w, 0, 0], [w, h, 0], [0, h, 0], [0.0, 0, 0]])
    ptsInit = pts[:, :2]

    # translate
    pts[:, 0] -= w/2
    pts[:, 1] -= h/2

    # rotate
    pts[:, 2] = pts[:, 0] * math.sin(angle)
    pts[:, 0] *= math.cos(angle)
    
    # proj
    pts[:, 0] *= (1 + pts[:, 2] / (w+h))
    pts[:, 1] *= (1 + pts[:, 2] / (w+h))

    # untranslate
    pts[:, 0] += w
    pts[:, 1] += h

    img2 = transform_image(img, (2*w, 2*h), pts[:, :2], ptsInit)

    plt.imshow(img2)
    plt.waitforbuttonpress(0.1)

    return
    plt.axis("equal")
    plt.plot(pts[:, 0], pts[:, 1])
    plt.waitforbuttonpress(0.1)
    print(pts)

if __name__ == "__main__":
    img = Image.open("panneaux_officiels/C28_None.png").convert("RGB").resize((1000, 1000))
    for i in range(10):
        rot_3D(img, i / 10)
    plt.show()
    exit()
    img2 = transform_image(
        img, 
        (100, 100), 
        [(10, 10), (90, 10), (10, 90), (90, 90)],
        [(0, 0), (100, 0), (0, 100), (100, 100)],
        )
    plt.imshow(img2)
    plt.show()