#!/usr/bin/env python
# script to import tweets
# You should not need to edit this file.

import time

import utils
import hits


def process_records(method,label):
    print 'starting %s'%label
    records = utils.read_records()
    start_time = time.time()
    method(records)
    end_time = time.time()
    print 'done with %s after %.3f seconds'%(label,end_time-start_time)

def main():
    indexer=hits.HITS()
    process_records(indexer.index_actors,'index')


if __name__=="__main__":
    main()
