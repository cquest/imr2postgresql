# script d'import des données IMR des Greffes des Tribunaux de Commerce

Ces scripts (bash et python) importent le stock et les flux de mise à jour dans une base postgresql

La base contient 7 tables:
- imr_pm : pour les personnes morales
- imr_pp : pour les personnes physiques (entreprises individuelles)
- imr_ets: pour les établissements
- imr_rep : pour les représentants des personnes morales
- imr_obs : pour les observations
- imr_actes : pour la liste des actes déposés
- imr-annuels : pour le liste des dépôts de comptes annuels


## Installation

pip3 install -r requirements.txt


## Utilisation

