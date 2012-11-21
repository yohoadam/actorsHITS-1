## crawler/

Contains scripts used to compile movie and actor information from a local PostgreSQL database.

##### create_actors_json.py
Script used to pull all relevant actor information from the local database and output the information to separate JSON-formatted files. Each line outputted to the file contains an actor's:
+ name
+ database ID
+ a genre list that includes the movie IDs of movies in each genre that feature the actor
+ a movie list containing the database ID, title, rating, vote count, genre list, and director(s) information for every movie featuring the actor.

##### create_movies_json.py

##### create_random_movies_json.py
