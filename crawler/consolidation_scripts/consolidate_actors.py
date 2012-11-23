# Consolidate all actor information by removing any repeated values and outputting the
# result to a single actors file.
#
# usage: python consolidate_actors.py <actor_info.json>
#
# actor_info.json - JSON-formatted file containing all actor information gathered so far.
#     Can contain repeats, which this program will ultimately remove.
#
# Author: Adam Yoho
# 21 November 2012

import json
import sys
import utils

from operator import itemgetter

if len(sys.argv) < 2:
    print '\nMissing input argument!\n'
    print '\tusage:', sys.argv[0], '<actor_info.json>\n'
    quit()

actor_id_set = set()
actor_list = []

OUTPUT_DIR = ''

valid_string = ''  # JSON-formatted string of all actors ready to be dumped to a file
reps = 0

# Read in all of the actor information collected
print 'consolidating actor info...'
actors = utils.read_file(sys.argv[1])
for actor in actors:
    actor_id = actor['id']
    if actor_id not in actor_id_set:
        actor_id_set.add(actor_id)
        actor_list.append(actor)
    else:
        reps += 1

print '(', len(actor_id_set), 'unique items,', reps, 'repeats removed )'

# Sort all actors by database ID to keep things ordered
print 'sorting...'
sorted_actors = sorted(actor_list, key=itemgetter('id'))

print 'creating JSON string to dump...'
for actor in sorted_actors:
    valid_string += json.dumps(actor) + '\n'
print 'done!\n'

# Write valid actors to a file
actor_filename = OUTPUT_DIR + 'all_recorded_actors.json'
print 'writing', actor_filename, '...'
mov_file = open(actor_filename, 'w')
mov_file.write(valid_string)
mov_file.close()
print

