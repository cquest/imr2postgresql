#! /bin/env python3
import csv
import sys
import re
import yaml

import psycopg2
from unidecode import unidecode

pg = psycopg2.connect("dbname=imr")

# définition du mapping des flux et des requêtes
fluxdef = yaml.load(open('imr.yml','r'))
flux = re.sub('^.*/','',sys.argv[1]).split('_')
if len(flux)>3 and '_'+flux[4]+'_' in fluxdef:
    curdef = fluxdef['_'+flux[4]+'_']
    if curdef['query'] == 'UPDATE':
        query = """WITH rows AS (UPDATE %s SET (@COLS@) = (@VALS@) WHERE @WHERE@ RETURNING 1)
                SELECT count(*) as updated FROM rows""" % curdef['table']
    else:
        query = """WITH rows AS (INSERT INTO %s (@COLS@) VALUES (@VALS@) RETURNING 1)
                SELECT count(*) as updated FROM rows""" % curdef['table']

    nb = 0
    with open(sys.argv[1],encoding = 'utf-8-sig') as csvfile:
        with pg:
            db = pg.cursor()
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                q = query
                sql_cols = ''
                sql_vals = ''
                sql_where = ''
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
                        sql_vals = sql_vals + db.mogrify("%s, ", (row[key],)).decode()
                q = q.replace('@COLS@', sql_cols[:-1]).replace('@VALS@', sql_vals[:-2] )
                if 'csv2sql' in curdef:
                    q = q.replace('@WHERE@', sql_where[:-5] )
                db.execute(q)
                rows = db.fetchone()
                if rows[0] != 1:
                    if rows[0] == 0 and flux[4] in ['6', '7', '9']:
                        # cas des nouveaux établissements figurant dans les EVT (voir doc page 25 et 30)
                        # faire un INSERT au lieu de l'UPDATE
                        q = re.sub(r'UPDATE (.*) SET ', 'INSERT INTO \g<1> ', q)
                        q = re.sub(r' = ', ' VALUES ', q)
                        q = re.sub(r' WHERE .* RETURNING ', ' RETURNING ', q)
                        db.execute(q)
                        rows = db.fetchone()
                    else:
                        print('%s|%s|%s|%s' % (sys.argv[1], sql_where[:-5], re.sub(r'\n *',' ',q), rows[0]))
                nb = nb + rows[0]
