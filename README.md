# Journal Officieux - Parsing & backend

Le code ci présent a pour but de collecter les données du Journal Officiel
français, de les analyser et de les ajouter à une base de données.

## Installation

Certaines dépendances Python sont requises pour exécuter les scripts de ce repo,
il suffit d'exécuter la commande suivante pour les installer :
```
pip3 install -r requirements.txt
```

## Exécution du code

* Une instance ElasticSearch (>= 6.0.2) doit être démarrée sur la machine sur laquelle
vous exécutez le code actuel.
* Ensuite, il suffit d'exécuter le commande suivante depuis la racine du repo :
```
python3 main.py config/default.yml
```

Cela aura pour effet de télécharger les données depuis le serveur FTP de la DILA
(Direction de l'Information Légale et Administrative) et de peupler votre
instance Elastic avec ces données.

## Accessibilité des données

Ce code sert en particulier à maintenir une instance ElasticSearch qui est
accessible à l'adresse https://api.jo.parlement-ouvert.fr.
Celle-ci est requêtable et vous pouvez disposer des données à votre guise.
