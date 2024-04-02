# Gestion des environnements en python

installation :

```
sudo apt-get install python3.10-venv
pip3 install pip-tools
```

## Géstion d'environnement

Pour créer un nouvel environnement:

```
python -m venv ${dossier}
```

Pour activer l'envirinnement:

```
source ${dossier}/bin/activate # pour activer
source ${dossier}/bin/desactivate # pour désactiver
```

## Gestion des dépendences

On spécifie les dépendences dans le fichier `requirements.in` selon la syntaxe suivante:

```
#requirements.in
numpy==1.26.4
pandas==2.2.1
```

On peut alors installer le tout avec la commande 
```
pip-compile     # génère la liste des dépendences
pip-sync        # télécharge, [dés]installe les dépendence 
```