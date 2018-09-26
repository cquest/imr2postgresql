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
    psql $DB -c "TRUNCATE imr_$table"
    psql $DB -c "CREATE INDEX imr_siren_$table on imr_$table (siren)"
    psql $DB -c "CREATE INDEX imr_greffe_$table on imr_$table (codegreffe, numerogestion)"
done
rm $TEMP/0101*.csv

# chargement (parallélisé) des fichiers stock CSV dans postgresql
rm $TEMP/*.csv
for z in $DATA/IMR_Donnees_Saisies/tc/stock/2017/05/04/*.zip
do
    echo $z
    unzip -q -d $TEMP $z
    f=$(ls -1v $TEMP/*.csv)
    echo $f | sed 's/ /\n/g' | parallel sh imr_copy.sh "{}" $DB
    rm $TEMP/*.csv
done

