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

def arange(mini:float, maxi:float, steps:int=50) -> np.ndarray:
    return np.array(range(steps))*(maxi-mini)/(steps-1) + mini

def find_motif_scale(
        img: Image.Image, 
        motif: Image.Image, 
        size_img:float|None=None, 
        dz_rel_max:float=1, 
        dz_rel_min:float=0.3, 
        dz_steps:int=8,
        rel_from_img:bool=True,
        ) -> tuple[float, float, float, float]:
    l_dz_rel = arange(dz_rel_min, dz_rel_max, dz_steps)
    l_dz_wh = np.zeros((dz_steps, 2))
    if rel_from_img:
        l_dz_wh[:,0] = l_dz_rel * img.size[0]
        l_dz_wh[:,1] = l_dz_rel * img.size[0] * motif.size[1] / motif.size[0]
    else:
        l_dz_wh[:,0] = l_dz_rel * motif.size[0]
        l_dz_wh[:,1] = l_dz_rel * motif.size[1]
    l_correl = np.array([find_motif_speed(img, motif.resize((int(dz_w), int(dz_h))), size_img) for (dz_w, dz_h) in l_dz_wh])
    i_corr_max = np.argmax(l_correl[:, 2])
    x, y, corr = l_correl[i_corr_max, :]
    dz = l_dz_wh[i_corr_max, 1]
    return x, y, dz, corr
