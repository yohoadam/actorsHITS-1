# Some helper functions.

import ujson
import fileinput

def read_records():
    for line in fileinput.input():
        yield ujson.loads(line)

