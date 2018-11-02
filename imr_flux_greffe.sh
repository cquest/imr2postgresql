echo $1
rm -f $1/*/*.temp $1/*/*_out.csv $1/*/*_err.csv
find $1 -name *.gz -exec gunzip {} \;
for f in $(ls -1v $1/*/*.csv)
do
  # est-ce-que le quoting du CSV est incorrect (nombre impair de ")?
  badquot=$(sed 's/""//g;s/"[^"]*"//g' "$f" | grep -c '"')
  if [ $badquot -gt 0 ]
  then
    echo "CLEAN $f"
    clean=$(echo $f | sed 's/.csv/_out.csv/')
    csvclean "$f" -d ';' -u 0 1>/dev/null
    csvformat -D ';' -U 0 $clean | \
      sed 's/Dénomination;Siren/Dénomination;Siren2/;s/Dénomination";"Siren/Dénomination";"Siren2/' \
      > "$f.temp"
  else
    sed 's/Dénomination;Siren/Dénomination;Siren2/' $f > "$f.temp"
  fi
  # gzip -9 "$f" &
  python imr.py "$f.temp"
  # compression des fichiers traités pour archivage
done
rm -f $1/*/*.temp $1/*/*_out.csv # $1/*/*_err.csv
