# Script for outputting needed information about ALL movies to JSON files.
# Pulls movie information from a local PostgreSQL database.
#
# Author: Adam Yoho
# 15 November 2012

import json
import settings
import sys
from imdb import IMDb
from imdb import Person
from imdb import Movie

print 'getting database access object...'
ia = IMDb('sql', uri='postgres://localhost/imdb', adultSearch=0)
print 'connected!\n'

movie_dict = {}

OUTPUT_DIR = '/root/Documents/csce470/Final_Project/json_movies/'
INV_OUTPUT_DIR = '/root/Documents/csce470/Final_Project/json_non_movies/'
ERROR_OUTPUT_DIR = '/root/Documents/csce470/Final_Project/repo/actorsHITS/crawler/'

PRINT_INTERVAL = 250     # After how many loop iterations should a status be output
RECORD_INTERVAL = 100    # How many movies should be recorded per file

MAX_MOVIE_ID = settings.MAX_TITLE_ID  # The highest ID value in the 'title' database table
START_ID = 1             # Start gathering movie information at this ID
END_ID = MAX_MOVIE_ID

sub_file_string = ''     # JSON-formatted string of all valid movies ready to be dumped to a file
invalid_string = ''      # JSON-formatted string of all non-movies looked up
movies_recorded = 0
invalid_movie_count = 0  # Keep count of number of non-movies found
invalid_file_num = 1

id = START_ID   # Initialize the id variable to where we wish to begin searching
start_id = id   # Records which ID the current subset of movies ready to be dumped starts at

while id <= END_ID:
    try:
        movie = ia.get_movie(id)
        if movie == None or (movie.get('kind') != 'movie' and movie.get('kind') != 'tv movie' and movie.get('kind') != 'video movie' and movie.get('kind') != 'tv mini series'):
            # Not a valid movie
            inv_movie = {'id':id}
            invalid_string += json.dumps(inv_movie) + '\n'
            invalid_movie_count += 1
            id += 1
            continue

        title = movie.get('long imdb title')
        if id % PRINT_INTERVAL == 0:
            print 'Looking up ID {0} of {1}\t({2:.1%}, {3:.3%} of total):\t'.format(id, END_ID, float(id-START_ID+1)/(END_ID-START_ID), float(id)/MAX_MOVIE_ID), u'{0}'.format(title)

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
            invalid_movie_count += 1
            id += 1
            continue

        movie_dict[id] = {'id':id, 'title':title, 'rating':rating, 'votes':votes, 'genres':genres, 'director':director_dict}

        # Add movie info to string to be output to a file later
        sub_file_string += json.dumps(movie_dict[id]) + '\n'

        movies_recorded += 1

        # Write the current movie subset to a file, then continue
        if movies_recorded % RECORD_INTERVAL == 0:
            subfilename = OUTPUT_DIR + 'sub_movies_' + str(start_id) + '-' + str(id) + '.json'
            print '\nwriting', subfilename, '...'
            sub_file = open(subfilename, 'w')
            sub_file.write(sub_file_string)
            sub_file.close()
            print
            # Update which ID the next subset of movies to be dumped will start at
            start_id = id + 1
            sub_file_string = ''

        # Write the invalid titles found to a file
        if invalid_movie_count % RECORD_INTERVAL == 0:
            subfilename = INV_OUTPUT_DIR + 'sub_non_movies_' + str(invalid_file_num) + '.json'
            print '\nwriting', subfilename, '...'
            sub_file = open(subfilename, 'w')
            sub_file.write(invalid_string)
            sub_file.close()
            print
            invalid_movie_count = 0
            invalid_file_num += 1
            invalid_string = ''

        id += 1

    except:
        error = 'Error (ID:' + str(id) + '):' + str(sys.exc_info()) + '\n'
        err_file = open(ERROR_OUTPUT_DIR + 'movie_load_errors.txt', 'a')
        err_file.write(error)
        err_file.close()
        id += 1
        pass

# Write the residual movies to a file
subfilename = OUTPUT_DIR + 'sub_movies_' + str(start_id) + '-' + str(id-1) + '.json'
print '\nwriting', subfilename, '...'
sub_file = open(subfilename, 'w')
sub_file.write(sub_file_string)
sub_file.close()
print

# Write the residual invalid titles to a file
inv_filename = INV_OUTPUT_DIR + 'sub_non_movies_' + str(invalid_file_num) + '.json'
print 'dumping non-movies', inv_filename, '...'
invalid_file = open(inv_filename, 'w')
invalid_file.write(invalid_string)
invalid_file.close()
print
