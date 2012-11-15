# Some helper functions.
# You should not need to edit this file.

#import ujson
import json
import fileinput



def read_records():
    for line in fileinput.input():
        yield json.loads(line)

def connect_db(dbname, remove_existing=False):
    pass
    '''
    con = connection.Connection(settings['mongo_host'],settings['mongo_port'])
    if remove_existing:
        con.drop_database(dbname)
    return con[dbname]
    '''


