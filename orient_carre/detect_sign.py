from find_motif import *
import matplotlib.pyplot as plt

__path__ = "/".join(__file__.split("/")[:-1])

class DetectionData:
    position: tuple[float,float]
    size: tuple[float, float]
    sub_detect: list["DetectionData"]

    def __init__(
            this, 
            position:tuple[float,float], 
            size: tuple[float, float]):
        this.position = position
        this.size = size
        this.sub_detect = []

    def add_sub_detect(this, sub:"DetectionData") -> None:
        this.sub_detect.append(sub)

    def show(this, ax=plt) -> None:
        x, y = this.position
        sx, sy = this.size
        ax.plot(
            [x-sx/2, x-sx/2, x+sx/2, x+sx/2, x-sx/2], 
            [y-sy/2, y+sy/2, y+sy/2, y-sy/2, y-sy/2])
        for sub in this.sub_detect:
            sub.show(ax)

def get_official_sign_img(code:str, value:None|str) -> Image.Image:
    return Image.open(f"{__path__}/panneaux_officiels/{code}_{value}.png").convert("RGB")

def detect_panneau(img:Image.Image, code:str, value:None|str) -> DetectionData:
    # get motif
    motif = get_official_sign_img(code, value)
    wM, hM = motif.size

    # compute position and size
    x, y, dz, corr = find_motif_scale(img, motif, size_img=64)
    x, y, dz, corr = find_motif_scale(img, motif.resize((round(dz*wM/hM), round(dz))), dz_rel_min=0.8, dz_rel_max=1.2, rel_from_img=False)
    detection = DetectionData([x, y], [dz*wM/hM, dz])

    # resize motif
    motif_resized = motif.resize((round(dz*wM/hM), round(dz)))

    # match angles
    wM, hM = motif_resized.size
    # NW
    crop = motif_resized.crop([0, 0, wM/4, hM/4])
    x, y, corr = find_motif(img, crop)
    detection.add_sub_detect(DetectionData([x, y], [wM/4, hM/4]))
    # NE
    crop = motif_resized.crop([3*wM/4, 0, wM, hM/4])
    x, y, corr = find_motif(img, crop)
    detection.add_sub_detect(DetectionData([x, y], [wM/4, hM/4]))
    # SW
    crop = motif_resized.crop([0, 3*hM/4, wM/4, hM])
    x, y, corr = find_motif(img, crop)
    detection.add_sub_detect(DetectionData([x, y], [wM/4, hM/4]))
    # SE
    crop = motif_resized.crop([3*wM/4, 3*hM/4, wM, hM])
    x, y, corr = find_motif(img, crop)
    detection.add_sub_detect(DetectionData([x, y], [wM/4, hM/4]))

    return detection

if __name__ == "__main__":
    import os
    path = f"{__path__}/../DATA_BASE_SIMULEE/C28"
    for name in os.listdir(path)[0:1]:
        img = Image.open(f"{path}/{name}").convert("RGB")
        data = detect_panneau(img, "C28", None)
        plt.clf()
        plt.imshow(img)
        data.show()
        plt.waitforbuttonpress()