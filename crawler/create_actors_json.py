# Script for outputting ALL relevant actors' information to a JSON file.
# Pulls actor information from a local PostgreSQL database.
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

movie_dict = {}

# Read in all of the offline movie information collected
print 'reading offline movie info...'
movies = utils.read_records()
for movie in movies:
    movie_id = movie['id']
    if movie_id not in movie_dict:
        movie_dict[movie_id] = movie
print 'done!\n'

# Connect to the database
print 'getting database access object...'
ia = IMDb('sql', uri='postgres://localhost/imdb', adultSearch=0)
print 'connected!\n'

#OUTPUT_DIR = '/root/Documents/csce470/Final_Project/json_actors/'
OUTPUT_DIR = '/root/Documents/csce470/Final_Project/repo/actorsHITS/crawler/'
ERROR_OUTPUT_DIR = '/root/Documents/csce470/Final_Project/repo/actorsHITS/crawler/'

PRINT_INTERVAL = 100     # After how many loop iterations should a status be output
RECORD_INTERVAL = 100    # How many actors should be recorded per file

MAX_PERSON_ID = settings.MAX_NAME_ID  # The highest ID value in the 'name' database table
START_ID = 1             # Start gathering actor information at this ID
END_ID = MAX_PERSON_ID

sub_file_string = ''     # JSON-formatted string of all valid movies ready to be dumped to a file
actors_recorded = 0

id = START_ID
start_id = id  # Records which ID the current subset of actors ready to be dumped starts at

while id <= END_ID:
    try:
        person = ia.get_person(id)
        if person == None:
            id += 1
            continue

        name = person.get('name')
        if id % PRINT_INTERVAL == 0:
            print 'Looking up ID {0} of {1}\t({2:.1%}, {3:.3%} of total):\t'.format(id, END_ID, float(id-START_ID+1)/(END_ID-START_ID), float(id)/MAX_PERSON_ID), u'{0}'.format(name)

        # Set up dictionary for recording actor's information
        actor_dict = { 'id':id, 'name':name, 'genre_list':{}, 'movies':{} }

        # Look up filmography
        films = person.get('actor') or person.get('actress')
        if films == None:
            id += 1
            continue

        movie_list = []
        genre_set = set()

        for film in films:
            # Only look up actual movies
            if film.get('kind') == 'movie':
                title = film.get('long imdb title')
                director_dict = {}

                movie_id = film.getID()
                if movie_id not in movie_dict:
                    # Only fetch the movie from the database if we haven't already
                    movie = ia.get_movie(movie_id)
                    director = movie.get('director')
                    if director != None and director != []:
                        for d in director:
                            director_dict[d.getID()] = d.get('name')
                else:
                    movie = movie_dict[movie_id]
                    for dir_id in movie.get('director'):
                        director_dict[dir_id] = movie.get('director')[dir_id]

                rating = movie.get('rating')
                votes = movie.get('votes')
                genres = movie.get('genres')

                if rating == None or votes == None or genres == None or genres == []:
                    # We can only deal with movies that have this information
                    continue

                actor_dict['movies'][movie_id] = {'id':movie_id, 'title':title, 'rating':rating, 'votes':votes, 'genres':genres, 'director:':director_dict}

                # Update universal movie dictionary
                if movie_id not in movie_dict:
                    movie_dict[movie_id] = actor_dict['movies'][movie_id]

                # Record the movie ID of each movie in each genre
                for genre in genres:
                    if genre in actor_dict['genre_list']:
                        actor_dict['genre_list'][genre].append(movie_id)
                    else:
                        actor_dict['genre_list'][genre] = [movie_id]

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

        id += 1

    except:
        error = 'Error (ID:' + str(id) + '):' + str(sys.exc_info()) + '\n'
        err_file = open(ERROR_OUTPUT_DIR + 'load_errors.txt', 'a')
        err_file.write(error)
        err_file.close()
        id += 1
        pass

# Write the residual subset of actors to a file
subfilename = OUTPUT_DIR + 'sub_actors_' + str(start_id) + '-' + str(id-1) + '.json'
print '\nwriting', subfilename, '...'
sub_file = open(subfilename, 'w')
sub_file.write(sub_file_string)
sub_file.close()
print
