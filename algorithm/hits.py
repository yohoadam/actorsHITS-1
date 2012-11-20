# Calculate the HITS values for all of the actors and movies in a file given to the script.
#
# usage: python hits.py actors_info.json
#
# Author: Heather Cheney
# 15 November 2012

import utils

from operator import itemgetter

def approx_equal(x, y, tolerance=1e-07):
    return abs(x-y) <= 0.5 * tolerance * (x + y)

class HITS(object):
    def __init__(self):
        self.actor_dict = {}
        self.movie_dict = {}
        self.actor_score_list = []
        self.MAX_HITS_ITERATIONS = 20

    def initialize(self, actors, genre):
        for actor_data in actors:
            if genre not in actor_data['genre_list'].keys():
                continue

            id = actor_data['id']

            total = 0

            for movie_id in actor_data['movies'].keys():
                if genre in actor_data['movies'][movie_id]['genres']:

                    # Add this movie's rating to the actor's overall score
                    total += actor_data['movies'][movie_id]['rating']

                    # Add this movie's information to dictionary of all movies
                    if not self.movie_dict.has_key(movie_id):
                        rating = actor_data['movies'][movie_id]['rating']
                        self.movie_dict[movie_id] = {'score': rating, 'actors': [], 'prev_score': rating}

                    self.movie_dict[movie_id]['actors'].append(id)

                    if not self.actor_dict.has_key(id):
                        # Initialize this actor in the actor dictionary
                        self.actor_dict[id] = {'name': actor_data['name'], 'score': 0.0, 'movies': [], 'prev_score': 0.0}

                    self.actor_dict[id]['movies'].append(movie_id)

            # Initialize the actor's authority score
            self.actor_dict[id]['score'] = float(total) / len(self.actor_dict[id]['movies'])
            self.actor_dict[id]['prev_score'] = float(total) / len(self.actor_dict[id]['movies'])

    def index_actors(self, actors_info):
        for actor in list(actors_info)[0]:
            print '%s %s genres covered: %s'%(actor.get('id'),actor.get('name'),' '.join(actor.get('genre_list')))
            for movies in actor.get('movies',[]):
                print ' -----> %s %s %d %s'%(movies.get('title'),movies.get('id'),movies.get('rating'),' '.join(movies.get('genres')))

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
            for movie_id in self.movie_dict.keys():
                prev_scores = []

                actors = self.movie_dict[movie_id]['actors']

                for actor in actors:
                    # Store the previous authority score of each actor
                    # NOTE: Since actors' scores have not yet been updated this iteration, the current score
                    # WILL BE the previous score
                    prev_scores.append(self.actor_dict[actor]['score'])

                # Record the previous hub score of this movie
                previous_score = self.movie_dict[movie_id]['prev_score']
                new_prev_score = self.movie_dict[movie_id]['score']
                self.movie_dict[movie_id]['prev_score'] = new_prev_score

                # Calculate the new hub score based on the previous authority score of each actor in the movie
                self.movie_dict[movie_id]['score'] = reduce(lambda x, y: x + y, prev_scores) / len(prev_scores)

                if not approx_equal(self.movie_dict[movie_id]['score'], previous_score):
                    # Keep iterating until hub scores converge
                    dirty = True

            # Update the authorities scores of all actors
            print 'calculating new authority(', iteration, ') scores...'
            for actor_id in self.actor_dict.keys():
                prev_scores = []

                movies = self.actor_dict[actor_id]['movies']

                for movie in movies:
                    # Store the previous hub score of each movie
                    prev_scores.append(self.movie_dict[movie]['prev_score'])

                # Record the previous authority score of this actor
                previous_score = self.actor_dict[actor_id]['prev_score']
                new_prev_score = self.actor_dict[actor_id]['score']
                self.actor_dict[actor_id]['prev_score'] = new_prev_score

                # Calculate the new authority score based on previouis hub score of each movie starred in
                self.actor_dict[actor_id]['score'] = reduce(lambda x, y: x + y, prev_scores) / len(prev_scores)

                if not approx_equal(self.actor_dict[actor_id]['score'], previous_score):
                    # Keep iterating until authority scores converge
                    dirty = True

                # Update the actor list that's used for sorting later
                actor_list.append({'id':actor_id, 'score':self.actor_dict[actor_id]['score']})

            iteration += 1

        self.actor_score_list = actor_list
        print

    def get_top_k_actors(self, k=10):
        return sorted(self.actor_score_list, key=itemgetter('score'), reverse=True)[:k]

if __name__ == '__main__':
    h = HITS()

    print 'reading actors file...\n'
    actors = utils.read_records()

    genre = 'Action'

    # Initialize the hubs and authorities scores
    print 'initializing scores for genre:', genre, '...\n'
    h.initialize(actors, genre)

    # Run HITS until convergence or MAX_HITS_ITERATIONS reached
    print 'running core algorithm...\n'
    h.core_algorithm()

    print 'outputting actor and movie dictionaries...\n'
    actor_list = []
    for id in h.actor_dict.keys():
        print h.actor_dict[id]['name'], ':\t', h.actor_dict[id]
        actor_list.append({ 'id':id, 'score':h.actor_dict[id]['score']})
    print

    for id in h.movie_dict.keys():
        print 'Movie', id, ':', h.movie_dict[id]
    print

    print 'sorting actors by score...\n'
    sorted_actors = h.get_top_k_actors()
    for actor in sorted_actors:
        #print 'Actor', actor['id'], ':', actor['score']
        print h.actor_dict[actor['id']]['name'], ':\t', actor['score']
    print

