# Calculate the HITS values for all of the actors and movies in a file given to the script.
#
# usage: python hits.py <genre_list.json> <movie_info_list.json> <actors_info.json> [genre]
#
# genre_list.json - JSON-formatted dictionaries with each genre tracked by IMDb as the only
#     key in each separate dict. One genre dict is specified per line.
# movie_list.json - JSON-formatted dictionaries with required invormation for all relevant
#     movies
# actors_info.json - JSON-formatted dictionaries with all actors' relevant information
# genre - String of a genre name for users to determine results of a single genre
#
# Author: Heather Cheney, Ananta Uprety, Adam Yoho
# 15 November 2012

import math
import settings
import sys
import utils

from imdb import IMDb
from operator import itemgetter

actor_dict = {}
genre_dict = {}
movie_dict = {}

DEFAULT_IMG = '/static/img/pic_anon.png'

def approx_equal(x, y, tolerance=1e-07):
    return abs(x-y) <= 0.5 * tolerance * (x + y)

def record_movies(movies):
    for movie in movies:
        movie_id = movie[settings.ID_K]
        movie_dict[movie_id] = movie

def record_data(actors):
    for actor in actors:
        actor_id = actor[settings.ID_K]

        # Add this actor to the universal actor dictionary
        if actor_id not in actor_dict:
            actor_dict[actor_id] = actor
            # Do not record all movie information again
            if settings.A_MOVIES_K in actor_dict[actor_id]:
                del actor_dict[actor_id][settings.A_MOVIES_K]

        for genre in actor[settings.A_GENRES_K]:
            # Add this actor's ID and movie list for this genre to the universal genre dictionary
            for movie_id in actor[settings.A_GENRES_K][genre]:
                if genre in genre_dict:
                    genre_dict[genre]['actor_set'].add(actor_id)
                    genre_dict[genre]['movie_set'].union(set(actor[settings.A_GENRES_K][genre]))
                else:
                    genre_dict[genre] = {'actor_set': set([actor_id]), 'movie_set': set(actor[settings.A_GENRES_K][genre])}

def apply_sigmoid(ind_var, numerator=1, sharpen_factor=1):
    # Sigmoid function that maps to the range [numerator / 2, numerator]
    return numerator / (1 + math.exp(sharpen_factor * -1 * ind_var))

def apply_sigmoid_through_origin(ind_var, numerator=1, sharpen_factor=1):
    # Sigmoid function that maps to the range [0, numerator]
    return (2 * (numerator / (1 + math.exp(sharpen_factor * -1 * ind_var)))) - numerator

class HITS(object):
    def __init__(self):
        self.actor_genre_dict = {}
        self.movie_genre_dict = {}
        self.actor_score_list = []
        self.total_genre_movies = 0
        # Concatenation of all genres with |
        self.genres = ''

        self.MAX_HITS_ITERATIONS = 10

    def reset(self):
        self.actor_genre_dict.clear()
        self.movie_genre_dict.clear()
        self.actor_score_list = []
        self.total_genre_movies = 0

    def calc_weighted_score(self, rating, votes, genre_movies_acted_in=0):
        # Adjust sharpness of weighting function
        # 0.001  : Reaches within 0.0001 of given rating value around 10,000 votes
        # 0.0005 : Reaches within 0.0001 of given rating value around 20,000 votes
        sharpen_factor = 0.0005

        # Use sigmoid function to give less weight to ratings with fewer votes
        rating_score = apply_sigmoid_through_origin(votes, (rating/10), sharpen_factor)

        # Ratings > 8.0 receive a bit of a bump, ratings < 8.0 get dampened a bit
        rating_score = rating_score * math.pow(((rating / 10) + 0.2), 3)

        movie_factor = 1
        if genre_movies_acted_in > 0:
            # Sigmoid function to further decrease weight for actors in very few movies
            movie_factor = apply_sigmoid_through_origin(genre_movies_acted_in, sharpen_factor=.2)

        return rating_score * movie_factor

    def initialize_scores(self, genre):
        if genre not in genre_dict:
            return

        self.reset()

        for actor_id in genre_dict[genre]['actor_set']:
            actor_data = actor_dict[actor_id]
            name = actor_data[settings.NAME_K]

            # Skip this actor if (s)he has been in no movies within this genre
            if genre not in actor_data[settings.A_GENRES_K]:
                continue

            total = 0
            num_genre_movies = len(set(actor_data[settings.A_GENRES_K][genre]))

            for movie_id in set(actor_data[settings.A_GENRES_K][genre]):
                title = movie_dict[movie_id][settings.TITLE_K]
                rating = movie_dict[movie_id][settings.RATING_K]
                votes = movie_dict[movie_id][settings.VOTES_K]

                # Add this movie's weighted score to the actor's overall score
                total += self.calc_weighted_score(rating, votes, num_genre_movies)

                self.total_genre_movies += 1

                # Add this movie's information to dictionary of all movies
                if not self.movie_genre_dict.has_key(movie_id):
                    score = self.calc_weighted_score(rating, votes)
                    self.movie_genre_dict[movie_id] = {'score': score, 'actors': [], 'prev_score': score}

                self.movie_genre_dict[movie_id]['actors'].append(actor_id)

                # Initialize this actor in the actor dictionary
                if not self.actor_genre_dict.has_key(actor_id):
                    self.actor_genre_dict[actor_id] = {'name': name, 'score': 0.0, 'movies': [], 'prev_score': 0.0}

                self.actor_genre_dict[actor_id]['movies'].append(movie_id)

            # Initialize the actor's authority score
            self.actor_genre_dict[actor_id]['score'] = total / num_genre_movies
            self.actor_genre_dict[actor_id]['prev_score'] = total / num_genre_movies

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
            #print 'calculating new hub(', iteration, ') scores...'
            for movie_id in self.movie_genre_dict.keys():
                prev_scores = []

                actors = self.movie_genre_dict[movie_id]['actors']

                for actor_id in actors:
                    # Store the previous authority score of each actor
                    # NOTE: Since actors' scores have not yet been updated this iteration, the current score
                    # WILL BE the previous score
                    prev_scores.append(self.actor_genre_dict[actor_id]['score'])

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
            #print 'calculating new authority(', iteration, ') scores...'
            for actor_id in self.actor_genre_dict.keys():
                prev_scores = []

                movies = self.actor_genre_dict[actor_id]['movies']

                for movie_id in movies:
                    # Store the previous hub score of each movie
                    prev_scores.append(self.movie_genre_dict[movie_id]['prev_score'])

                # Record the previous authority score of this actor
                previous_score = self.actor_genre_dict[actor_id]['prev_score']
                new_prev_score = self.actor_genre_dict[actor_id]['score']
                self.actor_genre_dict[actor_id]['prev_score'] = new_prev_score

                # Calculate the new authority score based on previous hub score of each movie starred in
                #self.actor_genre_dict[actor_id]['score'] = reduce(lambda x, y: x + y, prev_scores) / len(prev_scores)

                if not approx_equal(self.actor_genre_dict[actor_id]['score'], previous_score):
                    # Keep iterating until authority scores converge
                    dirty = True

                # Update the actor list that's used for sorting later
                actor_list.append({'id':actor_id, 'score':self.actor_genre_dict[actor_id]['score']})

            iteration += 1

        self.actor_score_list = actor_list

    def get_top_k_actors(self, k=10):
        return sorted(self.actor_score_list, key=itemgetter('score'), reverse=True)[:k]

    def get_actor_extras(self, genre, sorted_actor_list):
        actor_extras = {}

        for actor_info in sorted_actor_list:
            actor_id = actor_info[settings.ID_K]

            genre_movie_list = []
            director_counts = {}
            director_list = []

            # Collect information for each movie in the genre for this actor
            for movie_id in set(actor_dict[actor_id][settings.A_GENRES_K][genre]):
                movie_info = movie_dict[movie_id]

                # Record number of times actor has worked with this director
                movie_directors = movie_info[settings.DIRECTOR_K]
                for director_id in movie_directors:
                    if director_id in director_counts:
                        director_counts[director_id]['count'] += 1
                    else:
                        director_counts[director_id] = {'id': director_id, 'name': movie_directors[director_id], 'count': 1}

                genre_movie_list.append(movie_info)

            for director_id in director_counts:
                director_list.append(director_counts[director_id])

            # Sort top-rated movies and most frequent directors
            top_k = 5
            actor_top_movies = sorted(genre_movie_list, key=itemgetter('rating'), reverse=True)[:top_k]
            actor_freq_dirs = sorted(director_list, key=itemgetter('count'), reverse=True)[:top_k]

            actor_extras[actor_id] = {'top_movies': actor_top_movies, 'frequent_directors': actor_freq_dirs}

        return actor_extras

    def initialize_for_query(self, genre_file, movie_file, actors_file):
        print 'reading genre list...'
        self.genre_dicts = utils.read_file(genre_file)
        for genre in self.genre_dicts:
            self.genres += genre.keys()[0]
            self.genres += '|'

        print 'recording movie data...'
        movies = utils.read_file(movie_file)
        record_movies(movies)

        print 'reading actors file...'
        actors = utils.read_file(actors_file)
        record_data(actors)

    def query_hits(self, genre_query, top_k=30):
        if genre_query not in genre_dict:
            print 'No actors have any movies in this genre:', genre_query
            return []

        self.reset()

        # Initialize the hubs and authorities scores
        print 'initializing scores for genre:', genre_query, '...'
        self.initialize_scores(genre_query)

        # Run HITS until convergence or MAX_HITS_ITERATIONS reached
        print 'running core algorithm...'
        self.core_algorithm()

        print 'sorting actors by score...'
        sorted_actors = self.get_top_k_actors(top_k)

        print 'getting actor extra information...'
        actor_extras = self.get_actor_extras(genre_query, sorted_actors)

        result_list = []

        # Compile results
        for actor in sorted_actors:
            id = actor['id']
            name = self.actor_genre_dict[id]['name']
            num_movies = len(set(self.actor_genre_dict[id]['movies']))
            top_movies = actor_extras[id]['top_movies']
            top_movie_result = []
            for movie in top_movies:
                top_movie_result.append(movie['title']);

            directors = actor_extras[id]['frequent_directors']
            directors_result = []
            for director in directors:
                directors_result.append(director['name'])

            # For displaying a picture of the actor on the front end
            headshot_url = DEFAULT_IMG
            if settings.HEADSHOT_K in actor_dict[id]:
                headshot_url = actor_dict[id][settings.HEADSHOT_K]

            headshot_img_html = '<img width="100px" src="' + headshot_url + '" />'

            actor_info = { 'id': id, 'name': name, 'score': round(actor['score'], 5), 'movies': num_movies, 'top_movies': top_movie_result, 'frequent_directors': directors_result, 'headshot_url': headshot_url, 'headshot_img_html': headshot_img_html }
            result_list.append(actor_info)

        print 'number of results:', len(result_list)
        return result_list

if __name__ == '__main__':

    if len(sys.argv) < 4:
        print '\nMissing input argument!\n'
        print '\tusage:', sys.argv[0], '<genre_list.json> <movie_info_list.json> <actor_list.json> [genre]\n'
        quit()

    # Allow the user to select a genre at the command line
    user_genre = None
    if len(sys.argv) == 5:
        user_genre = sys.argv[4]

    h = HITS()

    print 'recording genre list...'
    genres = []
    genre_dicts = utils.read_file(sys.argv[1])
    for genre in genre_dicts:
        genres.append(genre[settings.GENRE_NAME_K])

    print 'recording movie data...'
    movies = utils.read_file(sys.argv[2])
    record_movies(movies)

    print 'recording actor data...'
    actors = utils.read_file(sys.argv[3])
    record_data(actors)

    for genre in genres:
        if user_genre != None:
            genre = user_genre

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
        sorted_actors = h.get_top_k_actors(k=30)

        # Record actor extras like best movies in this genre and directors most frequently worked with
        print 'looking up actor extras...'
        actor_extras = h.get_actor_extras(genre, sorted_actors)

        # Print results
        for actor in sorted_actors:
            actor_id = actor['id']
            print u'{:<25}'.format(h.actor_genre_dict[actor_id]['name']), ' : {:<10}'.format(actor['score']), '\tTotal movies:', len(h.actor_genre_dict[actor_id]['movies'])

            # Print top-rated movies
            print '\tTop movies:'
            for movie in actor_extras[actor_id]['top_movies']:
                print u'\t{:<35}'.format(movie['title'][:35]), '\tRating:', movie['rating'], '\tVotes: {:,}'.format(movie['votes'])
            print

            # Print directors worked with most frequently
            print '\tDirectors worked with most frequently:'
            for director in actor_extras[actor_id]['frequent_directors']:
                print u'\t{:<25}'.format(director['name']), '\tCount:', director['count']
            print

        if user_genre != None:
            break

