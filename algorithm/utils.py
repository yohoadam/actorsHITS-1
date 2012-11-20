# Some helper functions.

import json
import fileinput

def read_records():
    for line in fileinput.input():
        yield json.loads(line)

def read_file(file):
    for line in fileinput.input(file):
        yield json.loads(line)

def connect_db(dbname, remove_existing=False):
    pass
    '''
    con = connection.Connection(settings['mongo_host'],settings['mongo_port'])
    if remove_existing:
        con.drop_database(dbname)
    return con[dbname]
    '''


