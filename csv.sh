# header at top
cat $(find . -mindepth 1 -name '*.csv') |sort -u > all.csv.tmp
cat all.csv.tmp |grep "Build,Date" >all.csv
cat all.csv.tmp |grep -v "Build,Date" >>all.csv

python ../sow.py all.csv sow.csv

