# Script for outputting needed information from random movie samples to JSON files.
#
# Pulls movie information from a local PostgreSQL database. The valid ID range for movies
# in the database is split into a specified number of blocks (NUM_BLOCKS). A certain
# percentage (1 / SPREAD) of that block is then randomly selected to be retrieved and
# collectively output to JSON files.
#
# usage: python create_random_movies_json.py <movie_info.json> <invalid_movie_ids.json>
#
# movie_info.json - JSON-formatted file containing one entry per line that includes
#     movie ID, title, rating, genres, votes, and director(s)
# invalid_movie_ids.json - JSON-formatted file containing one entry per line that
#     includes the invalid movie ID
#
# Author: Adam Yoho
# 15 November 2012

import json
import random
import settings
import sys
import utils
from imdb import IMDb
from imdb import Person
from imdb import Movie

if len(sys.argv) < 3:
    print '\nMissing input argument!\n'
    print '\tusage:', sys.argv[0], '<movie_info.json> <invalid_movie_ids.json>\n'
    quit()

movie_dict = {}
inv_movie_set = set()

# Read in all of the offline movie information already collected
print 'reading offline movie info...'
movies = utils.read_file(sys.argv[1])
for movie in movies:
    movie_id = movie[settings.ID_K]
    if movie_id not in movie_dict:
        movie_dict[movie_id] = movie
print '\tread', len(movie_dict), 'valid movies'
print 'done!\n'

# Read in all of the offline invalid movie information already collected
print 'reading offline invalid movie IDs...'
inv_movies = utils.read_file(sys.argv[2])
for inv_movie in inv_movies:
    movie_id = inv_movie[settings.ID_K]
    if movie_id not in inv_movie_set:
        inv_movie_set.add(movie_id)
print '\tread', len(inv_movie_set), 'invalid movie IDs'
print 'done!\n'

print 'getting database access object...'
ia = IMDb('sql', uri='postgres://localhost/imdb', adultSearch=0)
print 'connected!\n'

OUTPUT_DIR = './random_json_movies/'
INV_OUTPUT_DIR = OUTPUT_DIR
ERROR_OUTPUT_DIR = ''   # Defaults to output errors in current directory

PRINT_INTERVAL = 100    # After how many loop iterations should a status be output
RECORD_INTERVAL = 100   # How many movies should be recorded per file
SPREAD = 5              # What percentage of each block should be randomly chosen

MAX_MOVIE_ID = settings.MAX_TITLE_ID  # The highest ID value in the 'title' database table
BASE_ID = 1             # The minimum ID in the range wishing to be partitioned

NUM_BLOCKS = 100
BLOCK_SIZE = (MAX_MOVIE_ID - BASE_ID) / NUM_BLOCKS

# Start searching at this ID (good for offsetting/restarting the script at different IDs)
START_ID = 1
END_ID = START_ID + BLOCK_SIZE

# If offsetting or restarting the script, skip the blocks already done
done_ids = START_ID - BASE_ID
blocks_pre_done = done_ids / BLOCK_SIZE
pre_blocks_accounted_for = False

# Get a random sample from blocks of IDs
for block in range(1 + blocks_pre_done, NUM_BLOCKS + 1):
    print 'Starting block', block, 'of', NUM_BLOCKS, '...'

    if block > 1 and (blocks_pre_done == 0 or pre_blocks_accounted_for):
        START_ID = END_ID + 1
        if block == NUM_BLOCKS:
            # Set the upper bound as the maximum ID for the last block
            END_ID = MAX_MOVIE_ID
        else:
            END_ID = START_ID + BLOCK_SIZE - 1

    # Ensure that the start and end bounds are valid
    if START_ID > MAX_MOVIE_ID:
        break
    if END_ID > MAX_MOVIE_ID:
        END_ID = MAX_MOVIE_ID

    # Record that any blocks pre-completed have now been accounted for
    pre_blocks_accounted_for = True

    # Pick some percentage of the range as random samples
    num_samples = (END_ID-START_ID) / SPREAD
    id_sample = random.sample(range(START_ID, END_ID+1), num_samples)

    # Reset variables for new block
    movies_recorded = 0
    file_num = 1          # Keep track of the current output file number for each block
    sub_file_string = ''  # JSON-formatted string of all valid movies ready to be dumped to a file
    invalid_string = ''   # JSON-formatted string of all invalid movies looked up
    cur_id_iteration = 0  # Keep track of how many IDs have been gone through in this block

    print 'starting id interval [', START_ID, ',', END_ID, '] (N =', num_samples, ')...'

    for id in id_sample:
        try:
            cur_id_iteration += 1

            if id in movie_dict or id in inv_movie_set:
                # Skip movies we have already looked up
                continue

            movie = ia.get_movie(id)
            if movie == None or (movie.get('kind') != 'movie' and movie.get('kind') != 'tv movie' and movie.get('kind') != 'video movie' and movie.get('kind') != 'tv mini series'):
                # Not a valid movie
                inv_movie = {settings.ID_K:id}
                invalid_string += json.dumps(inv_movie) + '\n'
                continue

            title = movie.get('long imdb title')
            if cur_id_iteration % PRINT_INTERVAL == 0:
                print 'Looking up ID {0} of {1}\t({2:.1%} through block):\t'.format(id, END_ID, float(cur_id_iteration)/num_samples), u'{0}'.format(title)

            rating = movie.get(settings.RATING_K)
            votes = movie.get(settings.VOTES_K)
            genres = movie.get(settings.M_GENRES_K)
            director = movie.get(settings.DIRECTOR_K)
            director_dict = {}
            if director != None and director != []:
                for d in director:
                    director_dict[d.getID()] = d.get(settings.NAME_K)

            if rating == None or votes == None or genres == None or genres == []:
                # We can only deal with movies that have this information
                inv_movie = {settings.ID_K:id}
                invalid_string += json.dumps(inv_movie) + '\n'
                continue

            movie_dict[id] = {settings.ID_K:id, settings.TITLE_K:title, settings.RATING_K:rating, settings.VOTES_K:votes, settings.M_GENRES_K:genres, settings.DIRECTOR_K:director_dict}

            # Add movie info to string to be output to a file later
            sub_file_string += json.dumps(movie_dict[id]) + '\n'

            movies_recorded += 1

            # Write the current movie subset to a file, then continue
            if movies_recorded % RECORD_INTERVAL == 0:
                subfilename = OUTPUT_DIR + 'sub_movies_b' + str(block) + '-' + str(file_num) + '.json'
                print '\nwriting', subfilename, '...'
                sub_file = open(subfilename, 'w')
                sub_file.write(sub_file_string)
                sub_file.close()
                print
                movies_recorded = 0
                file_num += 1
                sub_file_string = ''

        except:
            error = 'Error (ID:' + str(id) + '):' + str(sys.exc_info()) + '\n'
            err_file = open(ERROR_OUTPUT_DIR + 'random_movie_load_errors.txt', 'a')
            err_file.write(error)
            err_file.close()
            pass

    # Write the residual movies of this block to a file
    if sub_file_string != '':
        subfilename = OUTPUT_DIR + 'sub_movies_b' + str(block) + '-' + str(file_num) + '.json'
        print '\nwriting', subfilename, '...'
        sub_file = open(subfilename, 'w')
        sub_file.write(sub_file_string)
        sub_file.close()
        print

    # Write the invalid movies in this block to file
    if invalid_string != '':
        print 'dumping invalid movies in block', block, '...'
        inv_filename = INV_OUTPUT_DIR + 'random_inv_movies_block' + str(block) + '.json'
        invalid_file = open(inv_filename, 'w')
        invalid_file.write(invalid_string)
        invalid_file.close()
        print

