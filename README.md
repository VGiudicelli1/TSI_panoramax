# TSI_panoramax

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
- 5 full-time weeks

## Useful links

Export de test de panneaux détecté dans les photos de Panoramax:
https://www.data.gouv.fr/fr/datasets/export-de-test-de-panneaux-detecte-dans-les-photos-de-panoramax/

Modèle de données pour les panneaux de signalisation routière:
https://github.com/IGNF/Pano

Modèles de panneaux de signalisation routière en France:
https://fr.wikipedia.org/wiki/Panneau_de_signalisation_routière_en_France

API pour récupérer une photo avec son ID:
https://api.panoramax.xyz/api/pictures/<id>/hd.jpg 

Pour se renseigner - beta.gouv: 
https://beta.gouv.fr/

Sur la fabrique des géocommuns: 
https://www.ign.fr/institut/la-fabrique-des-geocommuns-incubateur-de-communs-lign

OSM:
- https://www.openstreetmap.fr/

Pour mieux connaitre Panoramax:
- https://panoramax.fr/
- https://forum.geocommuns.fr/

Pour découvrir le code:
- https://gitlab.com/geovisio

Pour tester la détection d'objet:
- https://github.com/panoramax-project/DetectionTutorial

## Dependencies

- [pyexiv2](https://github.com/LeoHsiao1/pyexiv2) - Version 2.12.0
- [pytest](https://github.com/pytest-dev/pytest) - Version 8.1.1
- [pillow](https://github.com/python-pillow/Pillow) - Version 10.3.0
- [numpy](https://github.com/numpy/numpy) - Version 1.26.4
