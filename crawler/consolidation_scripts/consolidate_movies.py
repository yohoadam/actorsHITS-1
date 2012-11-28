# Consolidate valid and invalid movie information by removing repeated values from each and
# outputting the result to two separate, ordered files.
#
# usage: python consolidate_movies.py <movie_info.json> <invalid_movie_info.json>
#
# movie_info.json - JSON-formatted file containing all valid movie information gained so far.
#     Can contain repeated movies, which this program will ultimately remove.
# invalid_movie_info.json - JSON-formatted file containing all IDs of invalid movies found
#     so far. Similarly to movie_info.json, repeats will ultimately be removed.
#
# Author: Adam Yoho
# 18 November 2012

import json
import sys
import utils

from operator import itemgetter

if len(sys.argv) < 3:
    print '\nMissing input argument!\n'
    print '\tusage:', sys.argv[0], '<movie_info.json> <invalid_movie_info.json>\n'
    quit()

movie_id_set = set()
movie_list = []
inv_movie_id_set = set()
inv_movie_list = []

OUTPUT_DIR = ''

valid_string = ''    # JSON-formatted string of all valid movies ready to be dumped to a file
invalid_string = ''  # JSON-formatted string of all invalid movies looked up
reps = 0             # Number of repeated movies
duals = 0            # Number of movies in both the valid and invalid lists

# Read in all of the offline movie information collected
print 'reading valid movie info...'
movies = utils.read_file(sys.argv[1])
for movie in movies:
    movie_id = movie['id']
    if movie_id not in movie_id_set:
        movie_id_set.add(movie_id)
        movie_list.append(movie)
    else:
        # Repeated movie ID; ignore
        reps += 1

print '({0:,} unique items, {1:,} repeats removed)'.format(len(movie_id_set), reps)

# Sort all movies by database ID to keep things ordered
sorted_movies = sorted(movie_list, key=itemgetter('id'))

print 'creating JSON string to dump...'
for movie in sorted_movies:
    valid_string += json.dumps(movie) + '\n'
print 'done!\n'

# Read in all of the offline invalid movie information collected
reps = 0
print 'reading invalid movie info...'
inv_movies = utils.read_file(sys.argv[2])
for inv_movie in inv_movies:
    movie_id = inv_movie['id']
    if movie_id in movie_id_set:
        # "Invalid" movie has already been counted as valid; do not record as invalid
        duals += 1
    elif movie_id not in inv_movie_id_set:
        inv_movie_id_set.add(movie_id)
        inv_movie_list.append(inv_movie)
    else:
        # Repeated movie ID; ignore
        reps += 1

print '({0:,} unique items, {1:,} repeats removed, {2:,} in both lists)'.format(len(inv_movie_id_set), reps, duals)

# Sort by database ID to keep things ordered
sorted_inv_movies = sorted(inv_movie_list, key=itemgetter('id'))

print 'creating JSON string to dump...'
for inv_movie in sorted_inv_movies:
    invalid_string += json.dumps(inv_movie) + '\n'
print 'done!\n'

# Write valid movies to a file
movie_filename = OUTPUT_DIR + 'all_recorded_movies.json'
print 'writing', movie_filename, '...'
mov_file = open(movie_filename, 'w')
mov_file.write(valid_string)
mov_file.close()
print

# Write invalid movie IDs to a file
inv_filename = OUTPUT_DIR + 'all_recorded_invalid_movies.json'
print 'dumping invalid movies', inv_filename, '...'
invalid_file = open(inv_filename, 'w')
invalid_file.write(invalid_string)
invalid_file.close()
print

