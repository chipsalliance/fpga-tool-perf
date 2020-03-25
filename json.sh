# header at top
echo $(find . -mindepth 1 -name 'meta.json') > all.json
python ../sow.py all.json sow.json

