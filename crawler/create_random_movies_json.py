# Script for outputting needed information from random movie samples to JSON files.
#
# Pulls movie information from a local PostgreSQL database. The valid ID range for movies
# in the database is split into a specified number of blocks (NUM_BLOCKS). A certain
# percentage (1 / SPREAD) of that block is then randomly selected to be retrieved and
# collectively output to JSON files.
#
# Author: Adam Yoho
# 15 November 2012

import json
import random
import settings
import sys
from imdb import IMDb
from imdb import Person
from imdb import Movie

print 'getting database access object...'
ia = IMDb('sql', uri='postgres://localhost/imdb', adultSearch=0)
print 'connected!\n'

movie_dict = {}

OUTPUT_DIR = '/root/Documents/csce470/Final_Project/random_json_movies/'
INV_OUTPUT_DIR = '/root/Documents/csce470/Final_Project/random_json_non_movies/'
ERROR_OUTPUT_DIR = '/root/Documents/csce470/Final_Project/repo/actorsHITS/crawler/'

PRINT_INTERVAL = 100    # After how many loop iterations should a status be output
RECORD_INTERVAL = 100   # How many movies should be recorded per file
SPREAD = 5              # What percentage of each block should be randomly chosen

MAX_MOVIE_ID = settings.MAX_TITLE_ID  # The highest ID value in the 'title' database table
BASE_ID = 1             # The minimum ID in the range wishing to be partitioned

NUM_BLOCKS = 100
BLOCK_SIZE = (MAX_MOVIE_ID - BASE_ID) / NUM_BLOCKS

# Start searching at this ID (good for offsetting/restarting the script at different IDs)
START_ID = BASE_ID
END_ID = START_ID + BLOCK_SIZE

# Get a random sample from blocks of IDs
for block in range(0,NUM_BLOCKS):
    print 'Starting block', block, 'of', NUM_BLOCKS, '...'

    if block > 0:
        START_ID = END_ID + 1
        END_ID = START_ID + BLOCK_SIZE - 1

    num_samples = (END_ID-START_ID) / SPREAD
    percentage = float(num_samples) / (END_ID-START_ID)

    # Pick some percentage of the range as random samples
    id_sample = random.sample(range(START_ID, END_ID+1), num_samples)

    # Reset variables for new block
    movies_recorded = 0
    file_num = 1          # Keep track of the current output file number for each block
    sub_file_string = ''  # JSON-formatted string of all valid movies ready to be dumped to a file
    invalid_string = ''   # JSON-formatted string of all non-movies looked up

    # Keep track of how many IDs have been gone through in this block
    cur_id_iteration = 0

    print 'starting id interval [', START_ID, ',', END_ID, ']...'
    for id in id_sample:
        try:
            cur_id_iteration += 1
    
            movie = ia.get_movie(id)
            if movie == None or (movie.get('kind') != 'movie' and movie.get('kind') != 'tv movie' and movie.get('kind') != 'video movie' and movie.get('kind') != 'tv mini series'):
                # Not a valid movie
                inv_movie = {'id':id}
                invalid_string += json.dumps(inv_movie) + '\n'
                continue
    
            title = movie.get('long imdb title')
            if id % PRINT_INTERVAL == 0:
                print 'Looking up ID {0} of {1}\t({2:.1%} through block):\t'.format(id, END_ID, float(cur_id_iteration)/num_samples), u'{0}'.format(title)
    
            rating = movie.get('rating')
            votes = movie.get('votes')
            genres = movie.get('genres')
            director = movie.get('director')
            director_dict = {}
            if director != None and director != []:
                for d in director:
                    director_dict[d.getID()] = d.get('name')
    
            if rating == None or votes == None or genres == None or genres == []:
                # We can only deal with movies that have this information
                inv_movie = {'id':id}
                invalid_string += json.dumps(inv_movie) + '\n'
                continue
    
            movie_dict[id] = {'id':id, 'title':title, 'rating':rating, 'votes':votes, 'genres':genres, 'director':director_dict}
    
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
    subfilename = OUTPUT_DIR + 'sub_movies_b' + str(block) + '-' + str(file_num) + '.json'
    print '\nwriting', subfilename, '...'
    sub_file = open(subfilename, 'w')
    sub_file.write(sub_file_string)
    sub_file.close()
    print

    # Write the non-movies in this block to file
    print 'dumping non-movies in block', block, '...'
    inv_filename = INV_OUTPUT_DIR + 'random_nonmovies_block' + str(block) + '.json'
    invalid_file = open(inv_filename, 'w')
    invalid_file.write(invalid_string)
    invalid_file.close()
    print
