import re
import os

JSON_FILE = os.environ['JSON_FILE']
CLEANED_FILE = os.environ['CLEANED_FILE']
MAX_NODES = os.environ['MAX_NODES']
NEO4J_IP = os.environ['NEO4J_IP']


def cleanString(jsonFile):
    # clean the string. Open the file as needed since it is too big to load into memory
    with open(jsonFile, 'r', encoding='utf-8') as f:
        with open('dblpExampleCleaned2.json', 'w', encoding='utf-8') as f2:
            length = f.seek(0, os.SEEK_END)
            i = 0
            for line in f:
                # regex to find all NumberInt(...) and replace it with the number inside of the parenthesis
                line = re.sub(r'NumberInt\((\d+)\)', r'\1', line)
                # remove all \\" in the string
                line = line.replace('\\"', '')
                # remove all \ in the string
                line = line.replace('\\', '')
                # escape all the ' in the string
                line = line.replace("'", "\\\\'")
                f2.write(line)
                # Show the progress
                if (i % 100000 == 0):
                    print('\r', end='')
                    print(f'Loading {round(i/length*100, 2)}%', end='')
                i +=1

def main():
    # clean the string
    cleanString(JSON_FILE)
