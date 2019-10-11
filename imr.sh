#! /bin/bash

TEMP=/dev/shm/imr
DATA=..
DB=imr

createdb $DB

mkdir -p $TEMP
unzip -n -d $DATA $DATA/IMR_Donnees_Saisies.zip

# création des tables SQL à partir des fichiers CSV stock du premier Tribunal de Commerce
unzip -n -d $TEMP $DATA/IMR_Donnees_Saisies/tc/stock/2017/05/04/0101_S1_20170504.zip
for f in $TEMP/0101*.csv
do
    # noms des colonnes
    cols=$(head -n 1 $f | sed 's/Dénomination;Siren/Dénomination;Siren2/;s/[_ ]//g;s/\.//g;s/-//g;s/é/e/g;s/è/e/g;s/ô/o/g;s/[^A-Za-z0-9;]//g;s/;/ text,/g;s/$/ text/')
    table=$(echo "$f" | sed 's/^.*_//;s/.csv//')
    psql $DB -c "DROP TABLE IF EXISTS imr_$table"
    psql $DB -c "CREATE TABLE imr_$table ($cols)"
done
rm $TEMP/0101*.csv

# chargement (parallélisé) des fichiers stock CSV initiaux dans postgresql
rm $TEMP/*.csv
for z in $DATA/IMR_Donnees_Saisies/tc/stock/2017/05/04/*.zip
do
    echo $z
    unzip -q -d $TEMP $z
    f=$(ls -1v $TEMP/*.csv)
    echo $f | sed 's/ /\n/g' | parallel sh imr_copy.sh "{}" $DB
    rm $TEMP/*.csv
done

# index unique pour clés primaires
psql $DB -c "
create unique index imr_pp_unique on imr_pp (codegreffe, numerogestion);
create unique index imr_pm_unique on imr_pm (codegreffe, numerogestion);
create unique index imr_ets_unique on imr_ets (codegreffe, numerogestion, idetablissement);
create unique index imr_rep_unique on imr_rep (codegreffe, numerogestion, idrepresentant, qualite);
create unique index imr_obs_unique on imr_obs (codegreffe, numerogestion, idobservation);
create unique index imr_annuels_unique on imr_annuels (codegreffe, numerogestion, numerodepot, datecloture);
"

# import des flux de mise à jour en parallèle...
for date in ../IMR_Donnees_Saisies/tc/flux/*/*/*
do
  ls -1v $date | parallel sh imr_flux_greffe.sh $date/{}
done
