import cv2 
from PIL import Image
import json
import pyexiv2

def get_xy_from_img_path(image_path):
    """
    Retrieves the x and y coordinates of the bbox from the image path
    in the image of origin.
    
    Args:
        image_path (str): The path to the image file.
        
    Returns:
        tuple: A tuple containing the x and y coordinates.
    """
    image = Image.open(image_path)
    if "comment" in image.info:
        comm = image.info["comment"]
        comm_json = json.loads(comm)
        xywh = comm_json.get('xywh')
        x, y = xywh[0], xywh[1]
        return x, y
    else:
        print('Pas de comm jpeg')

def get_wh_from_img_path(image_path):
    """
    Get the width and height of the original image from which the given image path
    is extracted.

    Args:
        image_path (str): The path to the image file.

    Returns:
        tuple: A tuple containing the width and height of the image.
    """
    image = pyexiv2.Image(image_path)
    xmp_data = image.read_xmp()
    image.close()
    width, height = xmp_data['Xmp.tiff.ImageWidth'], xmp_data['Xmp.tiff.ImageLength']
    return int(width), int(height)
    

def get_whxy_from_img_path(image_path):
    """
    Get the width, height of the original image, x&y coordinates of the bbox
    from the given image path.

    Parameters:
        image_path (str): The path of the image.

    Returns:
        tuple: A tuple containing the width, height, x-coordinate, and y-coordinate.
    """
    x,y = get_xy_from_img_path(image_path)
    w,h = get_wh_from_img_path(image_path)
    return w,h,x,y


print(get_whxy_from_img_path('/home/formation/Documents/bd_panneaux/test_crops_strasbourg/B14-50/0a5cc80d3de5d7bb2518677f6b305ebcc46a68fb9028a57947494243ebd3ff9e.jpg'))