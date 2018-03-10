# Journal Officieux - Parsing & backend

Le code ci présent a pour but de collecter les données du Journal Officiel
français, de les analyser et de les ajouter à une base de données.

## Exécution du code

* Une instance ElasticSearch (>= 6.0.2) doit être démarrée sur la machine sur laquelle
vous exécutez le code actuel.
* Ensuite, il suffit d'exécuter les commandes suivantes :
```cd parsing_xml
python3 fullDeploy.py
```

Certaines dépendances sont requises pour exécuter ce code, parmi lesquelles :
* elasticsearch (`pip3 install elasticsearch`)
* tqdm
* anytree

Cela aura pour effet de télécharger les données depuis le serveur FTP de la DILA
(Direction de l'Information Légale et Administrative) et de peupler votre
instance Elastic avec ces données.

## Accessibilité des données

Ce code sert en particulier à maintenir une instance ElasticSearch qui est
accessible à l'adresse https://api.jo.parlement-ouvert.fr.
Celle-ci est requêtable et vous pouvez disposer des données à votre guise.
