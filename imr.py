#! /bin/env python3
import csv
import sys
import re
import yaml

import psycopg2
from unidecode import unidecode


def load_fluxdef(filename):
    "chargement de la définition du mapping des flux et des requêtes"
    fluxdef = yaml.load(open('imr.yml','r'))
    flux = re.sub('^.*/','',filename).split('_')
    return(fluxdef, flux)


def make_query(sql_action, sql_table, sql_where, sql_cols, sql_vals):
    "Complète un template de requête SQL avec les WHERE / COLS / VALS"
    q = queries[sql_action].replace('@TABLE@', sql_table)
    q = q.replace('@COLS@', sql_cols[:-1]).replace('@VALS@', sql_vals[:-2] )
    q = q.replace('@WHERE@', sql_where[:-5])
    return(q)


# modèles de requêtes INSERT et UPDATE
queries = {'UPDATE': """WITH rows AS (UPDATE @TABLE@ SET (@COLS@) = (@VALS@) WHERE @WHERE@ RETURNING 1)
                        SELECT count(*) as updated FROM rows""",
           'INSERT': """WITH rows AS (INSERT INTO @TABLE@ (@COLS@) VALUES (@VALS@) RETURNING 1)
                        SELECT count(*) as updated FROM rows""",
           'DELETE': """WITH rows AS (DELETE FROM @TABLE@ WHERE @WHERE@ RETURNING 1)
                        SELECT count(*) as updated FROM rows"""}

fluxdef,flux = load_fluxdef(sys.argv[1])
if len(flux)>3 and '_'+flux[4]+'_' in fluxdef:
    nb = 0
    
    csvfile = open(sys.argv[1],encoding = 'utf-8-sig')
    pg = psycopg2.connect("dbname=imr")
    with pg:
        db = pg.cursor()
        reader = csv.DictReader(csvfile, delimiter=';', quoting=csv.QUOTE_NONE)
        for row in reader:
            curdef = fluxdef['_'+flux[4]+'_']

            # préparation des paramètres WHERE/COLS/VALS pour la requête SQL
            sql_where = ''
            sql_cols = ''
            sql_vals = ''
            for key in row:
                if 'csv2sql' in curdef and key in curdef['csv2sql']:
                    sql_where = (sql_where +
                                curdef['csv2sql'][key] +
                                db.mogrify(" = %s", (row[key],)).decode() +
                                " AND " )
                if row[key] != '':
                    field = re.sub(r'[ \_\-\.]','',unidecode(key)).lower()
                    sql_cols = sql_cols + field + ','
                    if row[key] in ['supprimé', '(supprimé)']:
                        row[key] = None
                    # forçage des dates en ISO sur les champs dateXXX
                    elif field[:4] == 'date':
                        row[key] = re.sub(r'([0-9]{2}).([0-9]{2}).([0-9]{4})',
                                        '\g<3>-\g<2>-\g<1>', row[key])
                    sql_vals = sql_vals + db.mogrify("%s, ", (row[key],)).decode()
            
            # sélection de la requête à exécuter
            action = curdef['query']
            # observations = ajout / rectification / suppression
            if flux[4] == '11':
                etat = row['Etat '] if 'Etat ' in row else row['Etat']
                if etat == 'Rectification':
                    action = 'UPDATE'
                elif etat == 'Suppression':
                    action = 'DELETE'
                else:
                    action = 'UPDATE'
            q = make_query(action, curdef['table'], sql_where, sql_cols, sql_vals)
            try:
                db.execute(q)
                rows = db.fetchone()
                if rows[0] != 1:
                    if rows[0] == 0 and flux[4] in ['6', '7', '9']:
                        # cas des nouveaux établissements figurant dans les EVT (voir doc page 25 et 30)
                        # faire un INSERT au lieu de l'UPDATE
                        q = make_query('INSERT', curdef['table'], sql_where, sql_cols, sql_vals)
                        db.execute(q)
                        rows = db.fetchone()
                    elif rows[0] > 1 :
                        print('DOUBLON: %s|%s|%s|%s' % (sys.argv[1], sql_where[:-5], re.sub(r'\n *',' ',q), rows[0]))
                nb = nb + rows[0]
            except:
                # l'INSERT a échoué... on tente un UPDATE
                if action == 'INSERT':
                    pg.commit()
                    q = make_query('UPDATE', curdef['table'], sql_where, sql_cols, sql_vals)
                    db.execute(q)
                    pass
                else:
                    print(curdef)
                    print(sys.argv[1])
                    print(sql_where[:-5])
                    print(re.sub(r'\n *',' ',q))
                    exit()
