import re
import os


def cleanString(jsonFile, destFile):
    print("Cleaning the json file...")
    # clean the string. Open the file as needed since it is too big to load into memory
    with open(jsonFile, 'r', encoding='utf-8') as f:
        with open(destFile, 'w', encoding='utf-8') as f2:
            length = f.seek(0, os.SEEK_END)
            # reset the file pointer to the beginning of the file
            f.seek(0, os.SEEK_SET)
            i = 0
            for line in f:
                # regex to find all NumberInt(...) and replace it with the number inside of the parenthesis
                line = re.sub(r'NumberInt\((\d+)\)', r'\1', line)
                # remove all \" in the string
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
            print('\r', end='')
    print("Done cleaning the json file")

# write the same thing, but using the command line and the sed command, by writing the command to a file and then executing it. SPlit each format into a separate function
def cleanString2(jsonFile, destFile):
    print("Cleaning the json file...")
    with open('sedCommand.sh', 'w') as f:
        f.write(f"sed -i 's/NumberInt(\\([0-9]\\+\\))/\\1/g' {jsonFile}\n")
        f.write(f"sed -i 's/\\\\\\\"//g' {jsonFile}\n")
        f.write(f"sed -i 's/\\\\//g' {jsonFile}\n")
        f.write(f"sed -i 's/\\'\/\\\\\\\\'\/g' {jsonFile}\n")


    os.system('sh sedCommand.sh')
    print("Done cleaning the json file")
