# TSI_panoramax
[![Test](https://github.com/VGiudicelli1/TSI_panoramax/actions/workflows/action.yml/badge.svg)](https://github.com/VGiudicelli1/TSI_panoramax/actions/workflows/action.yml)
## Project

The project `Panoramax` (https://panoramax.fr) is usualy presented as the OpenSource french version of Google Street View. It is a colaborative database of street georeferenced photographies. Around this main project, `Panneau(rama)x` extracts road signs from this database in order to update the `BD TOPO®` of IGN (https://geoservices.ign.fr/bdtopo).

This process takes place in several stages:

- Detect and classify road signs
- Geolocalize road sign
- Store in database

Our objectives are the last part of this project. We try to localize road signs with a convinient precision, and to manage dupplications before to create a `road signs database`

## Context

- 5 ENSG students
- TSI
- final project
- 4 full-time weeks

## Main Processes
[Associating cropped signs with the original images](./python/search_pi/insert-into-database.py)

[Computing center & height of signs](./python/trouver_centre_panneau.py)

Computing sign positions & removing duplicates : 
 - [Computes additional data](./algo_pos_panneau/main_compute_cropped_measurements.py)
 - [Clusterize](./algo_pos_panneau/main_clusterize.py)
 - [Computing sign position](./algo_pos_panneau/main_recompute_sign.py)


## Useful links

###### Sample export of detected signs in Panoramax pictures:
 - https://www.data.gouv.fr/fr/datasets/export-de-test-de-panneaux-detecte-dans-les-photos-de-panoramax/

###### Data model for road signs :
 - https://github.com/IGNF/Pano

###### List of french road signs:
 - https://fr.wikipedia.org/wiki/Panneau_de_signalisation_routière_en_France

###### API to get a specific Panoramax picture from its ID
 - https://api.panoramax.xyz/api/pictures/<id>/hd.jpg 

###### More infos - beta.gouv:
 - https://beta.gouv.fr/

### About:
###### Fabrique des géocommuns
 - https://www.ign.fr/institut/la-fabrique-des-geocommuns-incubateur-de-communs-lign

###### OSM:
- https://www.openstreetmap.fr/

###### Panoramax:
- https://panoramax.fr/
- https://forum.geocommuns.fr/

###### Check out the web interface code:
- https://gitlab.com/geovisio

###### Objet Detection:
- https://github.com/panoramax-project/DetectionTutorial

## Dependencies
- [attrs](https://github.com/python-attrs/attrs) - Version 23.2.0
- [certifi](https://github.com/certifi/python-certifi) - Version 2024.2.2
- [charset-normalizer](https://github.com/Ousret/charset_normalizer) - Version 3.3.2
- [contourpy](https://github.com/contourpy/contourpy) - Version 1.2.1
- [cycler](https://github.com/matplotlib/cycler) - Version 0.12.1
- [fonttools](https://github.com/fonttools/fonttools) - Version 4.51.0
- [idna](https://github.com/kjd/idna) - Version 3.7
- [iniconfig](https://github.com/pytest-dev/iniconfig) - Version 2.0.0
- [kiwisolver](https://github.com/nucleic/kiwi) - Version 1.4.5
- [matplotlib](https://github.com/matplotlib/matplotlib) - Version 3.8.3
- [numpy](https://github.com/numpy/numpy) - Version 1.26.4
- [opencv-python](https://github.com/opencv/opencv-python) - Version 4.9.0.80
- [packaging](https://github.com/pypa/packaging) - Version 24.0
- [pandas](https://github.com/pandas-dev/pandas) - Version 2.2.1
- [pillow](https://github.com/python-pillow/Pillow) - Version 10.3.0
- [pluggy](https://github.com/pytest-dev/pluggy) - Version 0.13.1
- [psycopg2](https://github.com/psycopg/psycopg2) - Version 2.9.9
- [py](https://github.com/pytest-dev/py) - Version 1.11.0
- [pyexiv2](https://github.com/LeoHsiao1/pyexiv2) - Version 2.12.0
- [pyparsing](https://github.com/pyparsing/pyparsing/) - Version 3.1.2
- [pyproj](https://github.com/pyproj4/pyproj) - Version 3.6.1
- [pytest](https://github.com/pytest-dev/pytest) - Version 6.2.4
- [python-dateutil](https://github.com/dateutil/dateutil) - Version 2.9.0.post0
- [pytz](https://github.com/stub42/pytz) - Version 2024.1
- [requests](https://github.com/psf/requests) - Version 2.31.0
- [scipy](https://github.com/scipy/scipy) - Version 1.13.0
- [six](https://github.com/benjaminp/six) - Version 1.16.0
- [toml](https://github.com/uiri/toml) - Version 0.10.2
- [tzdata](https://github.com/python/tzdata) - Version 2024.1
- [urllib3](https://github.com/urllib3/urllib3) - Version 2.2.1

