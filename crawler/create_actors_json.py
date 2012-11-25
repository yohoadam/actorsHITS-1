# Script for outputting all relevant actors' information to a JSON file.
# Pulls actor information from a local PostgreSQL database.
#
# usage: python create_actors_json.py <movie_info.json> <invalid_movie_ids.json>
#
# movie_info.json - JSON-formatted file containing one entry per line that includes
#     movie ID, title, rating, genres, votes, and director(s)
# invalid_movie_ids.json - JSON-formatted file containing one entry per line that
#     includes the invalid movie ID
#
# Author: Adam Yoho
# 15 November 2012

import json
import settings
import sys
import utils
from imdb import IMDb
from imdb import Person
from imdb import Movie

if len(sys.argv) < 3:
    print 'Missing input argument!\n'
    print '\tusage:', sys.argv[0], '<movie_info.json> <invalid_movie_ids.json>\n'
    quit()

movie_dict = {}
inv_movie_set = set()

# Read in all of the offline movie information collected
print 'reading offline movie info...'
movies = utils.read_file(sys.argv[1])
for movie in movies:
    movie_id = movie[settings.ID_K]
    if movie_id not in movie_dict:
        movie_dict[movie_id] = movie
print '\tread', len(movie_dict), 'valid movies'
print 'done!\n'

# Read in all of the offline invalid movie information collected
print 'reading offline invalid movie IDs...'
inv_movies = utils.read_file(sys.argv[2])
for inv_movie in inv_movies:
    movie_id = inv_movie[settings.ID_K]
    if movie_id not in inv_movie_set:
        inv_movie_set.add(movie_id)
print '\tread', len(inv_movie_set), 'invalid movie IDs'
print 'done!\n'

# Connect to the database
print 'getting database access object...'
ia = IMDb('sql', uri='postgres://localhost/imdb', adultSearch=0)
print 'connected!\n'

OUTPUT_DIR = './'        # Specify directory where actor files will be written
INV_OUTPUT_DIR = './'    # Specify directory where invalid movie IDs will be written
ERROR_OUTPUT_DIR = './'  # Specify directory to output errors

PRINT_INTERVAL = 100     # After how many loop iterations should a status be output
RECORD_INTERVAL = 100    # How many actors should be recorded per file

MAX_PERSON_ID = settings.MAX_NAME_ID  # The highest ID value in the 'name' database table
START_ID = 1             # Start gathering actor information at this ID
END_ID = MAX_PERSON_ID

actors_recorded = 0

sub_file_string = ''     # JSON-formatted string of all valid actors ready to be dumped to a file
new_movie_string = ''    # JSON-formatted string of all new movies looked up to be dumped to a file
invalid_string = ''      # JSON-formatted string of all invalid movies looked up
new_movie_count = 0      # Keep count of new movies found
new_movie_file_num = 1
invalid_movie_count = 0  # Keep count of invalid movies found
invalid_file_num = 1

id = START_ID
start_id = id  # Records which ID the current subset of actors ready to be dumped starts at

while id <= END_ID:
    try:
        person = ia.get_person(id)
        if person == None:
            id += 1
            continue

        name = person.get(settings.NAME_K)
        if id % PRINT_INTERVAL == 0:
            print 'Looking up ID {0} of {1}\t({2:.1%}, {3:.3%} of total):\t'.format(id, END_ID, float(id-START_ID+1)/(END_ID-START_ID), float(id)/MAX_PERSON_ID), u'{0}'.format(name)

        # Set up dictionary for recording actor's information
        actor_dict = { settings.ID_K:id, settings.NAME_K:name, settings.A_GENRES_K:{}, settings.A_MOVIES_K:{} }

        # Look up filmography
        films = person.get('actor') or person.get('actress')
        if films == None:
            id += 1
            continue

        movie_list = []
        genre_set = set()

        for film in films:
            # Only look up actual movies
            movie_id = film.getID()

            # Check if movie already found to be invalid
            if movie_id in inv_movie_set:
                continue

            if film.get('kind') != 'movie':
                # Record newly found invalid movies
                if movie_id not in inv_movie_set:
                    inv_movie_set.add(movie_id)
                    inv_movie = {settings.ID_K:movie_id}
                    invalid_string += json.dumps(inv_movie) + '\n'
                    invalid_movie_count += 1
                continue

            title = film.get('long imdb title')

            director_dict = {}

            if movie_id not in movie_dict:
                # Only fetch the movie from the database if we haven't already
                movie = ia.get_movie(movie_id)
                director = movie.get(settings.DIRECTOR_K)
                if director != None and director != []:
                    for d in director:
                        director_dict[d.getID()] = d.get(settings.NAME_K)
            else:
                movie = movie_dict[movie_id]
                directors = movie.get(settings.DIRECTOR_K)
                if directors and directors != {}:
                    for dir_id in directors.keys():
                        director_dict[dir_id] = movie.get(settings.DIRECTOR_K)[dir_id]

            rating = movie.get(settings.RATING_K)
            votes = movie.get(settings.VOTES_K)
            genres = movie.get(settings.M_GENRES_K)

            if rating == None or votes == None or genres == None or genres == []:
                # We can only deal with movies that have this information
                if movie_id not in inv_movie_set:
                    inv_movie_set.add(movie_id)
                    inv_movie = {settings.ID_K:movie_id}
                    invalid_string += json.dumps(inv_movie) + '\n'
                    invalid_movie_count += 1
                continue

            actor_dict[settings.A_MOVIES_K][movie_id] = {settings.ID_K:movie_id, settings.TITLE_K:title, settings.RATING_K:rating, settings.VOTES_K:votes, settings.M_GENRES_K:genres, settings.DIRECTOR_K:director_dict}

            # Update universal movie dictionary
            if movie_id not in movie_dict:
                movie_dict[movie_id] = actor_dict[settings.A_MOVIES_K][movie_id]
                new_movie_string += json.dumps(actor_dict[settings.A_MOVIES_K][movie_id]) + '\n'
                new_movie_count += 1

            # Record the movie ID of each movie in each genre
            for genre in genres:
                if genre in actor_dict[settings.A_GENRES_K]:
                    actor_dict[settings.A_GENRES_K][genre].append(movie_id)
                else:
                    actor_dict[settings.A_GENRES_K][genre] = [movie_id]

            # Update movies and genres this person has been in
            movie_list.append(movie_id)
            genre_set = genre_set.union(set(genres))

        if len(movie_list) == 0 or len(genre_set) == 0:
            # No required information found for this person
            id += 1
            continue

        # Add actor info to string to be output to a file later
        sub_file_string += json.dumps(actor_dict) + '\n'

        actors_recorded += 1

        # Write the current actor subset to a file, then continue
        if actors_recorded % RECORD_INTERVAL == 0:
            subfilename = OUTPUT_DIR + 'sub_actors_' + str(start_id) + '-' + str(id) + '.json'
            print '\nwriting', subfilename, '...'
            sub_file = open(subfilename, 'w')
            sub_file.write(sub_file_string)
            sub_file.close()
            print
            # Update which ID the next subset of movies to be dumped will start at
            start_id = id + 1
            sub_file_string = ''

        # Dump new, valid movies to file
        if new_movie_count >= RECORD_INTERVAL:
            new_mov_filename = OUTPUT_DIR + 'new_movies' + str(new_movie_file_num) + '.json'
            print '\ndumping new movies found...'
            new_mov_file= open(new_mov_filename, 'w')
            new_mov_file.write(new_movie_string)
            new_mov_file.close()
            print
            new_movie_string = ''
            new_movie_count = 0
            new_movie_file_num += 1

        # Dump invalid movie IDs to file
        if invalid_movie_count >= RECORD_INTERVAL:
            inv_filename = INV_OUTPUT_DIR + 'inv_movies' + str(invalid_file_num) + '.json'
            print '\ndumping invalid movies found...'
            inv_filename = open(inv_filename, 'w')
            inv_filename.write(invalid_string)
            inv_filename.close()
            print
            invalid_string = ''
            invalid_movie_count = 0
            invalid_file_num += 1

        id += 1

    except:
        error = 'Error (ID:' + str(id) + '):' + str(sys.exc_info()) + '\n'
        err_file = open(ERROR_OUTPUT_DIR + 'load_errors.txt', 'a')
        err_file.write(error)
        err_file.close()
        id += 1
        pass

# Write the residual subset of actors to a file
if sub_file_string != '':
    subfilename = OUTPUT_DIR + 'sub_actors_' + str(start_id) + '-' + str(id-1) + '.json'
    print '\nwriting', subfilename, '...'
    sub_file = open(subfilename, 'w')
    sub_file.write(sub_file_string)
    sub_file.close()
    print

# Write the residual new movies to a file
if new_movie_string != '':
    new_mov_filename = OUTPUT_DIR + 'new_movies' + str(new_movie_file_num) + '.json'
    print '\ndumping new movies found...'
    new_mov_file= open(new_mov_filename, 'w')
    new_mov_file.write(new_movie_string)
    new_mov_file.close()
    print

# Write the residual invalid movies to a file
if invalid_string != '':
    inv_filename = INV_OUTPUT_DIR + 'inv_movies' + str(invalid_file_num) + '.json'
    print '\ndumping invalid movies found...'
    inv_filename = open(inv_filename, 'w')
    inv_filename.write(invalid_string)
    inv_filename.close()
    print

