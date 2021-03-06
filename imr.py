#! /bin/env python3
import csv
import sys
import re
import yaml
import gzip
import json

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


def imr_log(infile, flux, action, table, sql_where_json=None, sql_cols=None, sql_vals=None):
    "Stockage des logs d'anomalies dans postgresql pour analyse"
    log = sql_where_json
    log["infile"] = infile
    log["flux"] = flux
    log["action"] = action
    log["table"] = table
    logfile.write(json.dumps(log)+'\n')


# modèles de requêtes INSERT et UPDATE
queries = {'UPDATE': """WITH rows AS (UPDATE @TABLE@ SET (@COLS@) = (@VALS@) WHERE @WHERE@ RETURNING 1)
                        SELECT count(*) as updated FROM rows""",
           'INSERT': """WITH rows AS (INSERT INTO @TABLE@ (@COLS@) VALUES (@VALS@) RETURNING 1)
                        SELECT count(*) as updated FROM rows""",
           'DELETE': """WITH rows AS (DELETE FROM @TABLE@ WHERE @WHERE@ RETURNING 1)
                        SELECT count(*) as updated FROM rows"""}

fluxdef,flux = load_fluxdef(sys.argv[1])
infile = re.sub('^.*/','',sys.argv[1])
logfile = open('logs/'+flux[0]+'.json', 'a')

if len(flux)>3 and '_'+flux[4]+'_' in fluxdef:
    nb = 0
    
    if sys.argv[1][-3:] == '.gz':
        csvfile = gzip.open(sys.argv[1])
    else:
        csvfile = open(sys.argv[1])

    # on lit la première ligne pour voire si on a des quotes ou pas...
    # head = csvfile.readline()
    # csvfile.seek(0, 0)
    # if '"' in head:
    #     reader = csv.DictReader(csvfile, delimiter=';')
    # else:
    #     reader = csv.DictReader(csvfile, delimiter=';', quoting=csv.QUOTE_NONE)
    reader = csv.DictReader(csvfile, delimiter=';')

    pg = psycopg2.connect("dbname=imr")
    with pg:
        db = pg.cursor()
        # a-t-on déjà intégré ce fichier ?
        db.execute('SELECT * FROM imr_csv WHERE greffe = %s AND lot >= %s AND fichier = %s', (flux[0], int(flux[1]), int(flux[4])))
        if db.rowcount > 0:
            # déjà intégré, on quitte
            exit()

        for row in reader:
            curdef = fluxdef['_'+flux[4]+'_']
            # préparation des paramètres WHERE/COLS/VALS pour la requête SQL
            sql_where = ''
            sql_where_json = {}
            sql_cols = ''
            sql_vals = ''
            for key in row:
                if row[key] is not None:
                    key2=key.replace('"','').replace('\ufeff','')
                    if 'csv2sql' in curdef and key2 in curdef['csv2sql']:
                        sql_where = (sql_where +
                                    curdef['csv2sql'][key2] +
                                    db.mogrify(" = %s", (row[key],)).decode() +
                                    " AND " )
                        sql_where_json[curdef['csv2sql'][key2]] = row[key]
                    if row[key] != '':
                        try:
                            field = re.sub(r'[ \_\-\.]','',unidecode(key2)).lower()
                        except:
                            print(sys.argv[1])
                            print(key, row)
                            exit()
                        sql_cols = sql_cols + field + ','
                        if row[key] in ['supprimé', '(supprimé)']:
                            row[key] = None
                        # forçage des dates en ISO sur les champs dateXXX
                        elif field[:4] == 'date' and row[key] is not None:
                            row[key] = re.sub(r'([0-9]{2}).([0-9]{2}).([0-9]{4})',
                                            '\g<3>-\g<2>-\g<1>', row[key])
                        sql_vals = sql_vals + db.mogrify("%s, ", (row[key],)).decode()

            # sélection de la requête à exécuter en fonction du libélle_evt ou état
            action = curdef['query']
            # rep = Nouveau / Modification
            if flux[4] == '6':
                etat = row['Libelle_Evt']
                if etat == 'Nouveau Dirigeant':
                    action = 'INSERT'
                else:
                    action = 'UPDATE'
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
                    if rows[0] == 0 and action == 'UPDATE':
                        # cas des nouveaux établissements figurant dans les EVT (voir doc page 25 et 30)
                        # faire un INSERT au lieu de l'UPDATE
                        q = make_query('INSERT', curdef['table'], sql_where, sql_cols, sql_vals)
                        db.execute(q)
                        rows = db.fetchone()
                        imr_log(infile, flux[4], 'UPDATE>INSERT', curdef['table'], sql_where_json)
                    elif rows[0] > 1 :
                        print('DOUBLON|%s|%s|%s|%s' % (infile, json.dumps(sql_where_json), re.sub(r'\n *',' ',q), rows[0]))
                nb = nb + rows[0]
            except:
                # l'INSERT a échoué... on tente un UPDATE
                if action == 'INSERT':
                    pg.commit()
                    q = make_query('UPDATE', curdef['table'], sql_where, sql_cols, sql_vals)
                    db.execute(q)
                    imr_log(infile, flux[4], 'INSERT>UPDATE', curdef['table'], sql_where_json)
                    pass
                else:
                    print(curdef)
                    print(sys.argv[1])
                    print(sql_where[:-5])
                    print(re.sub(r'\n *',' ',q))
            pg.commit()
        db.execute('INSERT INTO imr_csv (greffe, lot, fichier, quand) VALUES (%s, %s, %s, now())', (flux[0], int(flux[1]), int(flux[4])))
        pg.commit()
