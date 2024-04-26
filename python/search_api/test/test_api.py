import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from search_api import api
from search_api import csv_manager
from search_api import database
import json
import pandas as pd
string = '{"features": [{"id": "c41b9734-8e81-421f-b2cb-04aeec8250c1", "bbox": [7.731916, 48.50179, 7.731916, 48.50179], "type": "Feature", "links": [{"rel": "root", "href": "https://api.panoramax.xyz/api/", "type": "application/json", "title": "Instance catalog"}, {"rel": "parent", "href": "https://api.panoramax.xyz/api/collections/7ae92442-4594-4556-9730-4c955802e0dc", "type": "application/json"}, {"rel": "self", "href": "https://api.panoramax.xyz/api/collections/7ae92442-4594-4556-9730-4c955802e0dc/items/c41b9734-8e81-421f-b2cb-04aeec8250c1", "type": "application/geo+json"}, {"rel": "collection", "href": "https://api.panoramax.xyz/api/collections/7ae92442-4594-4556-9730-4c955802e0dc", "type": "application/json"}, {"rel": "license", "href": "https://www.etalab.gouv.fr/licence-ouverte-open-licence/", "title": "License for this object (etalab-2.0)"}, {"id": "e3195ad5-aa70-479c-b9df-1f22b8876c7f", "rel": "next", "href": "https://api.panoramax.xyz/api/collections/7ae92442-4594-4556-9730-4c955802e0dc/items/e3195ad5-aa70-479c-b9df-1f22b8876c7f", "type": "application/geo+json", "geometry": {"type": "Point", "coordinates": [7.731923, 48.50183]}}, {"id": "90c89c3c-f3fc-4101-a67e-b829419f7166", "rel": "prev", "href": "https://api.panoramax.xyz/api/collections/7ae92442-4594-4556-9730-4c955802e0dc/items/90c89c3c-f3fc-4101-a67e-b829419f7166", "type": "application/geo+json", "geometry": {"type": "Point", "coordinates": [7.731906, 48.501736]}}], "assets": {"hd": {"href": "https://panoramax-storage-public-fast.s3.gra.perf.cloud.ovh.net/main-pictures/c4/1b/97/34/8e81-421f-b2cb-04aeec8250c1.jpg", "type": "image/jpeg", "roles": ["data"], "title": "HD picture", "description": "Highest resolution available of this picture"}, "sd": {"href": "https://panoramax-storage-public-fast.s3.gra.perf.cloud.ovh.net/derivates/c4/1b/97/34/8e81-421f-b2cb-04aeec8250c1/sd.jpg", "type": "image/jpeg", "roles": ["visual"], "title": "SD picture", "description": "Picture in standard definition (fixed width of 2048px)"}, "thumb": {"href": "https://panoramax-storage-public-fast.s3.gra.perf.cloud.ovh.net/derivates/c4/1b/97/34/8e81-421f-b2cb-04aeec8250c1/thumb.jpg", "type": "image/jpeg", "roles": ["thumbnail"], "title": "Thumbnail", "description": "Picture in low definition (fixed width of 500px)"}}, "geometry": {"type": "Point", "coordinates": [7.731916, 48.50179]}, "providers": [{"name": "eurométropole de strasbourg", "roles": ["producer"]}, {"name": "Eurométropole de Strasbourg", "roles": ["producer"]}], "collection": "7ae92442-4594-4556-9730-4c955802e0dc", "properties": {"exif": {"Exif.Image.Model": "PULSAR", "Exif.Image.Artist": "Eurométropole de Strasbourg", "Exif.Image.GPSTag": "158", "Exif.Image.ExifTag": "100", "Exif.GPSInfo.GPSLatitude": "48501790/1000000 0/1 0/1", "Xmp.GPano.ProjectionType": "equirectangular", "Exif.GPSInfo.GPSDateStamp": "2022:05:30", "Exif.GPSInfo.GPSLongitude": "7731916/1000000 0/1 0/1", "Exif.GPSInfo.GPSTimeStamp": "17/1 23/1 19/1", "Exif.GPSInfo.GPSLatitudeRef": "N", "Exif.Photo.DateTimeOriginal": "2022-05-30T17:23:19.423000", "Exif.GPSInfo.GPSImgDirection": "255/100", "Exif.GPSInfo.GPSLongitudeRef": "E", "Exif.Photo.SubSecTimeOriginal": "423"}, "created": "2023-12-08T06:31:29.891408+00:00", "license": "etalab-2.0", "datetime": "2022-05-30T17:23:19.423000+00:00", "view:azimuth": 3, "geovisio:image": "https://panoramax-storage-public-fast.s3.gra.perf.cloud.ovh.net/main-pictures/c4/1b/97/34/8e81-421f-b2cb-04aeec8250c1.jpg", "geovisio:status": "ready", "geovisio:producer": "eurométropole de strasbourg", "geovisio:thumbnail": "https://panoramax-storage-public-fast.s3.gra.perf.cloud.ovh.net/derivates/c4/1b/97/34/8e81-421f-b2cb-04aeec8250c1/thumb.jpg", "original_file:name": "01522-1653923743-2022-05-30-15-23-19-423.jpg", "original_file:size": 4914653, "tiles:tile_matrix_sets": {"geovisio": {"type": "TileMatrixSetType", "title": "GeoVisio tile matrix for picture c41b9734-8e81-421f-b2cb-04aeec8250c1", "identifier": "geovisio-c41b9734-8e81-421f-b2cb-04aeec8250c1", "tileMatrix": [{"type": "TileMatrixType", "tileWidth": 687.5, "identifier": "0", "tileHeight": 687.5, "matrixWidth": 16, "matrixHeight": 8, "topLeftCorner": [0, 0], "scaleDenominator": 1}]}}, "pers:interior_orientation": {"camera_model": "PULSAR", "field_of_view": 360}}, "stac_version": "1.0.0", "asset_templates": {"tiles": {"href": "https://panoramax-storage-public-fast.s3.gra.perf.cloud.ovh.net/derivates/c4/1b/97/34/8e81-421f-b2cb-04aeec8250c1/tiles/{TileCol}_{TileRow}.jpg", "type": "image/jpeg", "roles": ["data"], "title": "HD tiled picture", "description": "Highest resolution available of this picture, as tiles"}}, "stac_extensions": ["https://stac-extensions.github.io/view/v1.0.0/schema.json", "https://stac-extensions.github.io/perspective-imagery/v1.0.0/schema.json", "https://stac-extensions.github.io/tiled-assets/v1.0.0/schema.json"]}], "links": []}'  
properties = json.loads(string)["features"][0]["properties"]

#Testing methods of api.py
def test_getClosestPictureInformation():
    assert(api.getClosestPictureInformation(7.731916,48.50179) == json.loads(
        '{"collectionId": "7ae92442-4594-4556-9730-4c955802e0dc", "pictureId": "c41b9734-8e81-421f-b2cb-04aeec8250c1", "lonPicture": 7.731916, "latPicture": 48.50179, "is360picture": true}'
        ))

def test_is360():
    assert(api.is360Picture(properties) == True)

def test_getShape():
    id = "90c89c3c-f3fc-4101-a67e-b829419f7166"
    assert(api.getShapePicture(id) == (11000, 5500))

#Testing methods of csv_manager.py
def test_extractCodeAndValue():
    data = pd.DataFrame({'directory': ['B14_50']})
    code, value = csv_manager.extractCodeAndValue(data.iloc[0])
    assert(code == "B14")
    assert(value == "50")
    data = pd.DataFrame({'directory': ['C12']})
    code, value = csv_manager.extractCodeAndValue(data.iloc[0])
    assert(code == "C12")
    assert(value == "null")

def reformatBbox():
    data = pd.DataFrame({'comment': ['{"xywh": [0, 0, 10, 10]}']})
    bbox = csv_manager.reformatBbox(data.iloc[0])
    assert(bbox == "[0,0,10,10]")

def test_getIntervalFromDate():
    dateBefore,dateAfter = csv_manager.getIntervalFromDate("2022:05:3017:23:19",5)
    assert(dateBefore == "2022-05-30T17:23:14Z")
    assert(dateAfter == "2022-05-30T17:23:24Z") 


if __name__ == "__main__":
    import pytest
    print(api.getClosestPictureInformation(7.731916,48.50179))
    pytest.main(["-vv", __file__])
