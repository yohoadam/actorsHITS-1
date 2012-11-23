# Calculate the HITS values for all of the actors and movies in a file given to the script.
#
# usage: python hits.py <genre_list.json> <actors_info.json>
#
# genre_list.json - JSON-formatted dictionaries with each genre tracked by IMDb as the only
#     key in each separate dict. One genre dict is specified per line.
#
# Author: Heather Cheney
# 15 November 2012

import settings
import sys
import utils

from operator import itemgetter

actor_dict = {}
genre_dict = {}

def approx_equal(x, y, tolerance=1e-07):
    return abs(x-y) <= 0.5 * tolerance * (x + y)

def record_data(actors):
    for actor in actors:
        actor_id = actor[settings.ID_K]

        # Add this actor to the universal actor dictionary
        if actor_id not in actor_dict:
            actor_dict[actor_id] = actor

        for genre in actor[settings.A_GENRES_K]:
            # Add this actor's ID and movie list for this genre to the universal genre dictionary
            for movie_id in actor[settings.A_GENRES_K][genre]:
                if genre in genre_dict:
                    genre_dict[genre]['actor_set'].add(actor_id)
                    genre_dict[genre]['movie_set'].union(set(actor[settings.A_GENRES_K][genre]))
                else:
                    genre_dict[genre] = {'actor_set': set([actor_id]), 'movie_set': set(actor[settings.A_GENRES_K][genre])}

class HITS(object):
    def __init__(self):
        self.actor_genre_dict = {}
        self.movie_genre_dict = {}
        self.actor_score_list = []
        self.total_genre_movies = 0

        self.MAX_HITS_ITERATIONS = 20

    def reset(self):
        self.actor_genre_dict.clear()
        self.movie_genre_dict.clear()
        self.actor_score_list = []
        self.total_genre_movies = 0

    def initialize_scores(self, genre):
        if genre not in genre_dict:
            return

        self.reset()

        for actor_id in genre_dict[genre]['actor_set']:
            actor_data = actor_dict[actor_id]

            # Skip this actor if (s)he has been in no movies within this genre
            if genre not in actor_data[settings.A_GENRES_K]:
                continue

            total = 0

            for movie_id in actor_data[settings.A_GENRES_K][genre]:
                # Add this movie's rating to the actor's overall score
                total += actor_data[settings.A_MOVIES_K][str(movie_id)][settings.RATING_K]

                self.total_genre_movies += 1

                # Add this movie's information to dictionary of all movies
                if not self.movie_genre_dict.has_key(movie_id):
                    rating = actor_data[settings.A_MOVIES_K][str(movie_id)][settings.RATING_K]
                    self.movie_genre_dict[movie_id] = {'score': rating, 'actors': [], 'prev_score': rating}

                self.movie_genre_dict[movie_id]['actors'].append(actor_id)

                if not self.actor_genre_dict.has_key(actor_id):
                    # Initialize this actor in the actor dictionary
                    self.actor_genre_dict[actor_id] = {'name': actor_data[settings.NAME_K], 'score': 0.0, 'movies': [], 'prev_score': 0.0}

                self.actor_genre_dict[actor_id]['movies'].append(movie_id)

            # Initialize the actor's authority score
            self.actor_genre_dict[actor_id]['score'] = float(total) / len(self.actor_genre_dict[actor_id]['movies'])
            self.actor_genre_dict[actor_id]['prev_score'] = float(total) / len(self.actor_genre_dict[actor_id]['movies'])

        print '\t', len(self.actor_genre_dict), 'actors'
        print '\t', self.total_genre_movies, 'total movies in this genre'
        if len(self.actor_genre_dict) > 0:
            print '\taverage movies per actor:', (float(self.total_genre_movies) / len(self.actor_genre_dict))

    def core_algorithm(self, iterations=None):
        iteration = 1
        if iterations is None:
            iterations = self.MAX_HITS_ITERATIONS

        actor_list = []

        dirty = True
        while dirty and iteration <= iterations:
            dirty = False
            actor_list = []

            # Update the hubs scores of all movies
            print 'calculating new hub(', iteration, ') scores...'
            for movie_id in self.movie_genre_dict.keys():
                prev_scores = []

                actors = self.movie_genre_dict[movie_id]['actors']

                for actor in actors:
                    # Store the previous authority score of each actor
                    # NOTE: Since actors' scores have not yet been updated this iteration, the current score
                    # WILL BE the previous score
                    prev_scores.append(self.actor_genre_dict[actor]['score'])

                # Record the previous hub score of this movie
                previous_score = self.movie_genre_dict[movie_id]['prev_score']
                new_prev_score = self.movie_genre_dict[movie_id]['score']
                self.movie_genre_dict[movie_id]['prev_score'] = new_prev_score

                # Calculate the new hub score based on the previous authority score of each actor in the movie
                self.movie_genre_dict[movie_id]['score'] = reduce(lambda x, y: x + y, prev_scores) / len(prev_scores)

                if not approx_equal(self.movie_genre_dict[movie_id]['score'], previous_score):
                    # Keep iterating until hub scores converge
                    dirty = True

            # Update the authorities scores of all actors
            print 'calculating new authority(', iteration, ') scores...'
            for actor_id in self.actor_genre_dict.keys():
                prev_scores = []

                movies = self.actor_genre_dict[actor_id]['movies']

                for movie in movies:
                    # Store the previous hub score of each movie
                    prev_scores.append(self.movie_genre_dict[movie]['prev_score'])

                # Record the previous authority score of this actor
                previous_score = self.actor_genre_dict[actor_id]['prev_score']
                new_prev_score = self.actor_genre_dict[actor_id]['score']
                self.actor_genre_dict[actor_id]['prev_score'] = new_prev_score

                # Calculate the new authority score based on previouis hub score of each movie starred in
                self.actor_genre_dict[actor_id]['score'] = reduce(lambda x, y: x + y, prev_scores) / len(prev_scores)

                if not approx_equal(self.actor_genre_dict[actor_id]['score'], previous_score):
                    # Keep iterating until authority scores converge
                    dirty = True

                # Update the actor list that's used for sorting later
                actor_list.append({'id':actor_id, 'score':self.actor_genre_dict[actor_id]['score']})

            iteration += 1

        self.actor_score_list = actor_list

    def get_top_k_actors(self, k=10):
        return sorted(self.actor_score_list, key=itemgetter('score'), reverse=True)[:k]

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print '\nMissing input argument!\n'
        print '\tusage:', sys.argv[0], '<genre_list.json> <actor_list.json>\n'
        quit()

    h = HITS()

    print 'reading genre list...'
    genres = []
    genre_dicts = utils.read_file(sys.argv[1])
    for genre in genre_dicts:
        genres.append(genre.keys()[0])

    print 'reading actors file...'
    actors = utils.read_file(sys.argv[2])
    record_data(actors)

    for genre in genres:
        print '-'*80
        print 'Genre:', genre, '\n'

        if genre not in genre_dict:
            print 'No actors have any movies in this genre!'
            continue

        h.reset()

        # Initialize the hubs and authorities scores
        print 'initializing scores for genre:', genre, '...'
        h.initialize_scores(genre)

        # Run HITS until convergence or MAX_HITS_ITERATIONS reached
        print 'running core algorithm...'
        h.core_algorithm()

        print 'sorting actors by score...'
        sorted_actors = h.get_top_k_actors(k=10)

        for actor in sorted_actors:
            print '{:<25}'.format(h.actor_genre_dict[actor['id']]['name']), ' : {:<10}'.format(actor['score']), '\tTotal movies:', len(h.actor_genre_dict[actor['id']]['movies'])

