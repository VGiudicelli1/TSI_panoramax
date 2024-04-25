from PIL import Image
import numpy as np
import cv2

def find_motif(
        img: Image.Image, 
        motif: Image.Image
        ) -> tuple[float, float, float]:
    correl = cv2.matchTemplate(np.array(img), np.array(motif), cv2.TM_CCORR_NORMED)
    y, x = np.unravel_index(np.argmax(correl, axis=None), correl.shape)
    c = correl[y, x]
    return x+motif.size[0]/2, y+motif.size[1]/2, c

def find_motif_speed(
        img: Image.Image, 
        motif: Image.Image, 
        size_img:float|None=64
        ) -> tuple[float, float, float]:
    if (size_img==None):
        return find_motif(img, motif)
    wm, hm = motif.size
    wi, hi = img.size
    scale = size_img / wi
    x, y, corr = find_motif(
        img.resize((int(wi*scale), int(hi*scale))),
        motif.resize((int(wm*scale), int(hm*scale)))
    )
    return x/scale, y/scale, corr

def find_motif_scale(
        img: Image.Image, 
        motif: Image.Image, 
        size_img:float|None=None, 
        dz_rel_max:float=1, 
        dz_rel_min:float=0.3, 
        dz_steps:int=8
        ) -> tuple[float, float, float, float]:
    l_dz_rel = np.arange(dz_rel_min, dz_rel_max, dz_steps)
    l_dz_wh = np.zeros((dz_steps, 2))
    l_dz_wh[:,0] = l_dz_rel * img.size[0]
    l_dz_wh[:,1] = l_dz_rel * img.size[0] * motif.size[1] / motif.size[0]
    l_correl = np.array([find_motif_speed(img, motif.resize(dz_w, dz_h), size_img) for (dz_w, dz_h) in l_dz_wh])
    x = 0
    y = 0
    dz = 0
    corr = 0
    return x, y, dz, corr


    # f varie entre 1 et 0.3
    fMax = 1
    fMin = 0.3

    for _ in range(3):
        n = 8
        lF = [(i*fMin + (n-i)*fMax)/n for i in range(n+1)]
        lC = np.array([max_correl(img, motif, s, f) for f in lF])
        i = min(6, max(1, np.argmax(lC[:, 0])))
        fMax = lF[i-1]
        fMin = lF[i+1]
    
    f = (fMax + fMin) / 2
    c, x, y = lC[i]
    return x, y, f*img.size[0]
    print(f, c, x, y)


