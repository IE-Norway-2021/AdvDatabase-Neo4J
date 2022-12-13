# using sed apply the following format to the file
# replace all NumberInt(...) with just the number, remove all \", remove all \ , escape all ' in the file

sed -i 's/NumberInt(//g' -i 's/)//g' -i 's/\"//g' -i 's/\\//g' -i "s/'/\'/g" 'dblpExample.json' > 'dblpExampleCleaned.json'