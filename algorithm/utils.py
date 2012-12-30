# Some helper functions.

import json
import fileinput

def read_records():
    for line in fileinput.input():
        yield json.loads(line)

def read_file(file):
    for line in fileinput.input(file):
        yield json.loads(line)

