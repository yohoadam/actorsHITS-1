#!/usr/bin/env python
# Script to test HITS algorithm

import unittest
import hits

ACTOR_CORPUS = [
    {
        "movies": {
            "1": {"rating": 8.0, "votes": 100000, "genres": ["Action", "Adventure"], "title": "MOVIE A"},
            "2": {"rating": 7.0, "votes": 50000, "genres": ["Comedy", "Drama"], "title": "MOVIE B"},
            "4": {"rating": 7.5, "votes": 75000, "genres": ["Action", "Sci-Fi"], "title": "MOVIE D"}
        },
        "genre_list": {"Action": [1, 4], "Adventure": [1], "Comedy": [2], "Drama": [2], "Sci-Fi": [4]},
        "id":1,
        "name": "Actor A"
    },
    {
        "movies": {
            "1": {"rating": 8.0, "votes": 100000, "genres": ["Action", "Adventure"], "title": "MOVIE A"},
            "4": {"rating": 7.5, "votes": 75000, "genres": ["Action", "Sci-Fi"], "title": "MOVIE D"}
        },
        "genre_list": {"Action": [1, 4], "Adventure": [1], "Sci-Fi": [4]},
        "id":2,
        "name": "Actor B"
    },
    {
        "movies": {
            "1": {"rating": 8.0, "votes": 100000, "genres": ["Action", "Adventure"], "title": "MOVIE A"},
            "3": {"rating": 9.5, "votes": 200000, "genres": ["Drama"], "title": "MOVIE C"}
        },
        "genre_list": {"Action": [1], "Adventure": [1], "Drama": [3]},
        "id":3,
        "name": "Actor C"
    },
    {
        "movies": {
            "1": {"rating": 8.0, "votes": 100000, "genres": ["Action", "Adventure"], "title": "MOVIE A"},
            "2": {"rating": 7.0, "votes": 50000, "genres": ["Comedy", "Drama"], "title": "MOVIE B"},
            "4": {"rating": 7.5, "votes": 75000, "genres": ["Action", "Sci-Fi"], "title": "MOVIE D"}
        },
        "genre_list": {"Action": [1, 4], "Adventure": [1], "Comedy": [2], "Drama": [2], "Sci-Fi": [4]},
        "id":4,
        "name": "Actor D"
    },
    {
        "movies": {
            "2": {"rating": 7.0, "votes": 50000, "genres": ["Comedy", "Drama"], "title": "MOVIE B"}
        },
        "genre_list": {"Comedy": [2], "Drama": [2]},
        "id":5,
        "name": "Actor E"
    },
    {
        "movies": {
            "2": {"rating": 7.0, "votes": 50000, "genres": ["Comedy", "Drama"], "title": "MOVIE B"},
            "3": {"rating": 9.5, "votes": 200000, "genres": ["Drama"], "title": "MOVIE C"}
        },
        "genre_list": {"Comedy": [2], "Drama": [2, 3]},
        "id":6,
        "name": "Actor F"
    },
    {
        "movies": {
            "3": {"rating": 9.5, "votes": 200000, "genres": ["Drama"], "title": "MOVIE C"}
        },
        "genre_list": {"Drama": [3]},
        "id":7,
        "name": "Actor G"
    },
    {
        "movies": {
            "3": {"rating": 9.5, "votes": 200000, "genres": ["Drama"], "title": "MOVIE C"},
            "4": {"rating": 7.5, "votes": 75000, "genres": ["Action", "Sci-Fi"], "title": "MOVIE D"}
        },
        "genre_list": {"Action": [4], "Drama": [3], "Sci-Fi": [4]},
        "id":8,
        "name": "Actor H"
    }
]

class TestHits(unittest.TestCase):
    def setUp(self):
        self.hits = hits.HITS()
        self.test_genre = 'Action'
        self.dec_accuracy = 14
        hits.actor_dict.clear()
        hits.genre_dict.clear()

    def reset_hits(self):
        hits.actor_dict.clear()
        hits.genre_dict.clear()
        self.hits.actor_genre_dict.clear()
        self.hits.movie_genre_dict.clear()
        self.hits.actor_score_list = []

    def test_empty_corpus(self):
        print '\ntesting empty corpus...\n'
        hits.record_data(iter([]))
        self.hits.initialize_scores(self.test_genre)
        self.assertEqual(len(self.hits.actor_genre_dict.keys()), 0)
        self.assertEqual(len(self.hits.movie_genre_dict.keys()), 0)

    def test_initialize(self):
        print '\ntesting initialization (', self.test_genre, ')...\n'
        hits.record_data(iter(ACTOR_CORPUS))
        self.hits.initialize_scores(self.test_genre)

        # Test that only actors with movies in the test genre appear
        self.assertTrue(1 in self.hits.actor_genre_dict)
        self.assertTrue(2 in self.hits.actor_genre_dict)
        self.assertTrue(3 in self.hits.actor_genre_dict)
        self.assertTrue(4 in self.hits.actor_genre_dict)
        self.assertTrue(8 in self.hits.actor_genre_dict)
        self.assertTrue(5 not in self.hits.actor_genre_dict)
        self.assertTrue(6 not in self.hits.actor_genre_dict)
        self.assertTrue(7 not in self.hits.actor_genre_dict)

        # Test that only movies that fall in the test genre appear
        self.assertTrue(1 in self.hits.movie_genre_dict)
        self.assertTrue(4 in self.hits.movie_genre_dict)
        self.assertTrue(2 not in self.hits.movie_genre_dict)
        self.assertTrue(3 not in self.hits.movie_genre_dict)

        # Test initial HITS scores
        self.assertEqual(self.hits.actor_genre_dict[1]['score'], 7.75)
        self.assertEqual(self.hits.actor_genre_dict[1]['prev_score'], 7.75)
        self.assertEqual(self.hits.actor_genre_dict[2]['score'], 7.75)
        self.assertEqual(self.hits.actor_genre_dict[2]['prev_score'], 7.75)
        self.assertEqual(self.hits.actor_genre_dict[3]['score'], 8)
        self.assertEqual(self.hits.actor_genre_dict[3]['prev_score'], 8)
        self.assertEqual(self.hits.actor_genre_dict[4]['score'], 7.75)
        self.assertEqual(self.hits.actor_genre_dict[4]['prev_score'], 7.75)
        self.assertEqual(self.hits.actor_genre_dict[8]['score'], 7.5)
        self.assertEqual(self.hits.actor_genre_dict[8]['prev_score'], 7.5)

        self.assertEqual(self.hits.movie_genre_dict[1]['score'], 8)
        self.assertEqual(self.hits.movie_genre_dict[1]['prev_score'], 8)
        self.assertEqual(self.hits.movie_genre_dict[4]['score'], 7.5)
        self.assertEqual(self.hits.movie_genre_dict[4]['prev_score'], 7.5)

    def test_core_algorithm(self):
        its = 2
        print '\ntesting core algorithm (', self.test_genre, ',', its, 'iterations )...\n'
        hits.record_data(iter(ACTOR_CORPUS))
        self.hits.initialize_scores(self.test_genre)
        self.hits.core_algorithm(iterations=its)

        # Test that only actors with movies in the test genre appear
        self.assertTrue(1 in self.hits.actor_genre_dict)
        self.assertTrue(2 in self.hits.actor_genre_dict)
        self.assertTrue(3 in self.hits.actor_genre_dict)
        self.assertTrue(4 in self.hits.actor_genre_dict)
        self.assertTrue(8 in self.hits.actor_genre_dict)
        self.assertTrue(5 not in self.hits.actor_genre_dict)
        self.assertTrue(6 not in self.hits.actor_genre_dict)
        self.assertTrue(7 not in self.hits.actor_genre_dict)

        # Test that only movies in the test genre appear
        self.assertTrue(1 in self.hits.movie_genre_dict)
        self.assertTrue(4 in self.hits.movie_genre_dict)
        self.assertTrue(2 not in self.hits.movie_genre_dict)
        self.assertTrue(3 not in self.hits.movie_genre_dict)

        # Test HITS scores
        self.assertEqual(self.hits.actor_genre_dict[1]['score'], 7.75)
        self.assertEqual(self.hits.actor_genre_dict[1]['prev_score'], 7.75)
        self.assertEqual(self.hits.actor_genre_dict[2]['score'], 7.75)
        self.assertEqual(self.hits.actor_genre_dict[2]['prev_score'], 7.75)
        self.assertEqual(self.hits.actor_genre_dict[3]['score'], 7.8125)
        self.assertEqual(self.hits.actor_genre_dict[3]['prev_score'], 8)
        self.assertEqual(self.hits.actor_genre_dict[4]['score'], 7.75)
        self.assertEqual(self.hits.actor_genre_dict[4]['prev_score'], 7.75)
        self.assertEqual(self.hits.actor_genre_dict[8]['score'], 7.6875)
        self.assertEqual(self.hits.actor_genre_dict[8]['prev_score'], 7.5)

        self.assertEqual(self.hits.movie_genre_dict[1]['score'], 7.8125)
        self.assertEqual(self.hits.movie_genre_dict[1]['prev_score'], 7.8125)
        self.assertEqual(self.hits.movie_genre_dict[4]['score'], 7.6875)
        self.assertEqual(self.hits.movie_genre_dict[4]['prev_score'], 7.6875)

    def test_core_algorithm_extended(self):
        its = 20
        print '\ntesting core algorithm (', self.test_genre, ',', its, 'iterations )...\n'
        hits.record_data(iter(ACTOR_CORPUS))
        self.hits.initialize_scores(self.test_genre)
        self.hits.core_algorithm(iterations=its)

        # Test that only actors with movies in the test genre appear
        self.assertTrue(1 in self.hits.actor_genre_dict)
        self.assertTrue(2 in self.hits.actor_genre_dict)
        self.assertTrue(3 in self.hits.actor_genre_dict)
        self.assertTrue(4 in self.hits.actor_genre_dict)
        self.assertTrue(8 in self.hits.actor_genre_dict)
        self.assertTrue(5 not in self.hits.actor_genre_dict)
        self.assertTrue(6 not in self.hits.actor_genre_dict)
        self.assertTrue(7 not in self.hits.actor_genre_dict)

        # Test that only movies in the test genre appear
        self.assertTrue(1 in self.hits.movie_genre_dict)
        self.assertTrue(4 in self.hits.movie_genre_dict)
        self.assertTrue(2 not in self.hits.movie_genre_dict)
        self.assertTrue(3 not in self.hits.movie_genre_dict)

        # Test HITS scores
        self.assertAlmostEqual(self.hits.actor_genre_dict[1]['score'], 7.75)
        self.assertAlmostEqual(self.hits.actor_genre_dict[1]['prev_score'], 7.75)
        self.assertAlmostEqual(self.hits.actor_genre_dict[2]['score'], 7.75)
        self.assertAlmostEqual(self.hits.actor_genre_dict[2]['prev_score'], 7.75)
        self.assertAlmostEqual(self.hits.actor_genre_dict[3]['score'], 7.75000023841858, places=self.dec_accuracy)
        self.assertAlmostEqual(self.hits.actor_genre_dict[3]['prev_score'], 7.75000095367432, places=self.dec_accuracy)
        self.assertAlmostEqual(self.hits.actor_genre_dict[4]['score'], 7.75)
        self.assertAlmostEqual(self.hits.actor_genre_dict[4]['prev_score'], 7.75)
        self.assertAlmostEqual(self.hits.actor_genre_dict[8]['score'], 7.74999976158142, places=self.dec_accuracy)
        self.assertAlmostEqual(self.hits.actor_genre_dict[8]['prev_score'], 7.74999904632568, places=self.dec_accuracy)

        self.assertAlmostEqual(self.hits.movie_genre_dict[1]['score'], 7.75000023841858, places=self.dec_accuracy)
        self.assertAlmostEqual(self.hits.movie_genre_dict[1]['prev_score'], 7.75000023841858, places=self.dec_accuracy)
        self.assertAlmostEqual(self.hits.movie_genre_dict[4]['score'], 7.74999976158142, places=self.dec_accuracy)
        self.assertAlmostEqual(self.hits.movie_genre_dict[4]['prev_score'], 7.74999976158142, places=self.dec_accuracy)

    def test_core_algorithm_drama(self):
        its = 20
        print '\ntesting core algorithm ( Drama ,', its, 'iterations )...\n'
        hits.record_data(iter(ACTOR_CORPUS))
        self.hits.initialize_scores('Drama')
        self.hits.core_algorithm(iterations=its)

        # Test that only actors with movies in the test genre appear
        self.assertTrue(1 in self.hits.actor_genre_dict)
        self.assertTrue(3 in self.hits.actor_genre_dict)
        self.assertTrue(4 in self.hits.actor_genre_dict)
        self.assertTrue(5 in self.hits.actor_genre_dict)
        self.assertTrue(6 in self.hits.actor_genre_dict)
        self.assertTrue(7 in self.hits.actor_genre_dict)
        self.assertTrue(8 in self.hits.actor_genre_dict)
        self.assertTrue(2 not in self.hits.actor_genre_dict)

        # Test that only movies in the test genre appear
        self.assertTrue(2 in self.hits.movie_genre_dict)
        self.assertTrue(3 in self.hits.movie_genre_dict)
        self.assertTrue(1 not in self.hits.movie_genre_dict)
        self.assertTrue(4 not in self.hits.movie_genre_dict)

        # Test HITS scores
        self.assertAlmostEqual(self.hits.actor_genre_dict[1]['score'], 8.17960810661316, places=self.dec_accuracy)
        self.assertAlmostEqual(self.hits.actor_genre_dict[1]['prev_score'], 8.15614414215088, places=self.dec_accuracy)
        self.assertAlmostEqual(self.hits.actor_genre_dict[3]['score'], 8.32039189338684, places=self.dec_accuracy)
        self.assertAlmostEqual(self.hits.actor_genre_dict[3]['prev_score'], 8.34385585784912, places=self.dec_accuracy)
        self.assertAlmostEqual(self.hits.actor_genre_dict[4]['score'], 8.17960810661316, places=self.dec_accuracy)
        self.assertAlmostEqual(self.hits.actor_genre_dict[4]['prev_score'], 8.15614414215088, places=self.dec_accuracy)
        self.assertAlmostEqual(self.hits.actor_genre_dict[5]['score'], 8.17960810661316, places=self.dec_accuracy)
        self.assertAlmostEqual(self.hits.actor_genre_dict[5]['prev_score'], 8.15614414215088, places=self.dec_accuracy)
        self.assertAlmostEqual(self.hits.actor_genre_dict[6]['score'], 8.25)
        self.assertAlmostEqual(self.hits.actor_genre_dict[6]['prev_score'], 8.25)
        self.assertAlmostEqual(self.hits.actor_genre_dict[7]['score'], 8.32039189338684, places=self.dec_accuracy)
        self.assertAlmostEqual(self.hits.actor_genre_dict[7]['prev_score'], 8.34385585784912, places=self.dec_accuracy)
        self.assertAlmostEqual(self.hits.actor_genre_dict[8]['score'], 8.32039189338684, places=self.dec_accuracy)
        self.assertAlmostEqual(self.hits.actor_genre_dict[8]['prev_score'], 8.34385585784912, places=self.dec_accuracy)

        self.assertAlmostEqual(self.hits.movie_genre_dict[2]['score'], 8.17960810661316, places=self.dec_accuracy)
        self.assertAlmostEqual(self.hits.movie_genre_dict[2]['prev_score'], 8.17960810661316, places=self.dec_accuracy)
        self.assertAlmostEqual(self.hits.movie_genre_dict[3]['score'], 8.32039189338684, places=self.dec_accuracy)
        self.assertAlmostEqual(self.hits.movie_genre_dict[3]['prev_score'], 8.32039189338684, places=self.dec_accuracy)

    def test_top_k(self):
        print '\ntesting top k actors...\n'
        top_k = 10
        its = 10

        # Test Action
        genre = 'Action'
        print '\ntesting top', top_k, '(', genre, ')...\n'
        hits.record_data(iter(ACTOR_CORPUS))
        self.hits.initialize_scores(genre)
        self.hits.core_algorithm(iterations=its)
        top_actors = self.hits.get_top_k_actors(top_k)

        self.assertEqual(top_actors[0]['id'], 3)
        self.assertEqual(top_actors[1]['id'], 1)
        self.assertEqual(top_actors[2]['id'], 2)
        self.assertEqual(top_actors[3]['id'], 4)
        self.assertEqual(top_actors[4]['id'], 8)

        self.reset_hits()

        # Test Drama
        genre = 'Drama'
        print '\ntesting top', top_k, '(', genre, ')...\n'
        hits.record_data(iter(ACTOR_CORPUS))
        self.hits.initialize_scores(genre)
        self.hits.core_algorithm(iterations=its)
        top_actors = self.hits.get_top_k_actors(top_k)

        self.assertEqual(top_actors[0]['id'], 3)
        self.assertEqual(top_actors[1]['id'], 7)
        self.assertEqual(top_actors[2]['id'], 8)
        self.assertEqual(top_actors[3]['id'], 6)
        self.assertEqual(top_actors[4]['id'], 1)
        self.assertEqual(top_actors[5]['id'], 4)
        self.assertEqual(top_actors[6]['id'], 5)

        self.reset_hits()

        # Test Adventure
        genre = 'Adventure'
        print '\ntesting top', top_k, '(', genre, ')...\n'
        hits.record_data(iter(ACTOR_CORPUS))
        self.hits.initialize_scores(genre)
        self.hits.core_algorithm(iterations=its)
        top_actors = self.hits.get_top_k_actors(top_k)

        self.assertEqual(top_actors[0]['id'], 1)
        self.assertEqual(top_actors[1]['id'], 2)
        self.assertEqual(top_actors[2]['id'], 3)
        self.assertEqual(top_actors[3]['id'], 4)

if __name__ == '__main__':
    unittest.main()
