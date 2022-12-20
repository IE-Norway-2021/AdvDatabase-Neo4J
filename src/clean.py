import re
import os


def cleanString(jsonFile, destFile, maxNodes):
    # clean the string. Open the file as needed since it is too big to load into memory
    one_line_before, two_lines_before, three_lines_before = '', '', ''
    numberOfNodesRead = 0
    with open(jsonFile, 'r', encoding='utf-8') as f:
        with open(destFile, 'w', encoding='utf-8') as f2:
            for line in f:
                if (']' in line):
                    # last one, we do nothing
                    pass
                elif ('title' in line and '_id' in one_line_before and '{' in two_lines_before and '},' in three_lines_before):
                    numberOfNodesRead += 1
                    if (numberOfNodesRead == maxNodes):
                        # write the end of the json file
                        f2.write('}]')
                        return

                # regex to find all NumberInt(...) and replace it with the number inside of the parenthesis
                line = re.sub(r'NumberInt\((\d+)\)', r'\1', line)
                # remove all \" in the string
                line = line.replace('\\"', '')
                # remove all \ in the string
                line = line.replace('\\', '')
                # escape all the ' in the string
                line = line.replace("'", "\\\\'")
                f2.write(three_lines_before)
                
                three_lines_before = two_lines_before
                two_lines_before = one_line_before
                one_line_before = line
            f2.write(three_lines_before)
            f2.write(two_lines_before)
            f2.write(one_line_before)

