cat $(find . -mindepth 1 -name '*.csv') |sort -u >all.csv
python ../sow.py all.csv sow.csv

