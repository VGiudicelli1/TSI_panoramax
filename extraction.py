from PIL import Image
import json
import pyexiv2

def get_whxy_from_img_path(image_path):
    """
    Retrieves the width and height of the image of origin ,
    as well as the x and y coordinates of the bbox from the image path
    in the image of origin.
    
    Args:
        image_path (str): The path to the image file.
        
    Returns:
        tuple: A tuple containing the width, height, x and y coordinates.
    """
    image = Image.open(image_path)
    if "comment" in image.info:
        comm = image.info["comment"]
        comm_json = json.loads(comm)
        xywh = comm_json.get('xywh')
        x, y = xywh[0], xywh[1]
        w, h = comm_json.get('width'), comm_json.get('height')
        return w,h,x,y
    else:
        print('Pas de comm jpeg')
        return None
