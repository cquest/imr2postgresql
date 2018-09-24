TEMP=/dev/shm/imr
DATA=..

mkdir -p $TEMP
unzip -n -d $DATA $DATA/IMR_Donnees_Saisies.zip

# création des tables SQL à partir des fichiers CSV stock du premier Tribunal de Commerce
unzip -n -d $TEMP $DATA/IMR_Donnees_Saisies/tc/stock/2017/05/04/0101_S1_20170504.zip
for f in $TEMP/0101*.csv
do
    # noms des colonnes
    cols=$(head -n 1 $f | sed 's/Dénomination;Siren/Dénomination;Siren2/;s/[_ ]//g;s/\.//g;s/-//g;s/é/e/g;s/è/e/g;s/ô/o/g;s/[^A-Za-z0-9;]//g;s/;/ text,/g;s/$/ text/')
    table=$(echo "$f" | sed 's/^.*_//;s/.csv//')
    psql -c "DROP TABLE IF EXISTS imr_$table"
    psql -c "CREATE TABLE imr_$table ($cols)"
    psql -c "TRUNCATE imr_$table"
    psql -c "CREATE INDEX imr_siren_$table on imr_$table (siren)"
    psql -c "CREATE INDEX imr_greffe_$table on imr_$table (codegreffe, numerogestion)"
done

# chargement des fichiers stock CSV dans postgresql
rm $TEMP/*.csv
for f in $DATA/IMR_Donnees_Saisies/tc/stock/2017/05/04/*.zip
do
    echo $f
    unzip -q -d $TEMP $f
    for f in $TEMP/*.csv
    do
       table=$(echo "$f" | sed 's/^.*_//;s/.csv//')
       psql -c "\copy imr_$table from '$f' with (format csv, header true, delimiter ';')"
    done
    rm $TEMP/*.csv
done

exit

# import flux de création
for table in PM PP rep ets obs annuels
do
    for f in $DATA/IMR_Donnees_Saisies/tc/flux/2017/05/*/*/*/*_$table.csv
    do
        echo $f
        psql -c "\copy imr_$table from '$f' with (format csv, header true, delimiter ';', quote '\\' )"
        mv $f $f.done
    done &
done


for table in PM PP rep ets obs annuels
do
  psql -c "create table if not exists imr_maj_$table as select * from imr_$table limit 1; truncate imr_maj_$table;"
done

# import flux de mise à jour
for table in PM_EVT PP_EVT rep_partant_EVT rep_nouveau_modifie_EVT ets_nouveau_modifie_EVT ets_supprime_EVT
do
    for f in $( ls -1v $DATA/IMR_Donnees_Saisies/tc/flux/2017/05/*/*/*/*_$table.csv)
    do
        table2=$(echo $table | sed 's/_.*_EVT//;s/_EVT//')
        echo "$f $table2"
        psql -c "\copy imr_maj_$table2 from '$f' with (format csv, header true, delimiter ';', quote '\\' )"
        #mv $f $f.done
    done &
done


for f in $(ls -1v $DATA/IMR_Donnees_Saisies/tc/flux/2017/05/18/*/*/*.csv)
do
    python imr.py "$f"
done
