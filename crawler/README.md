## crawler/

Contains scripts used to compile movie and actor information from a local PostgreSQL database.

##### create_actors_json.py
Script used to pull all relevant actor information from the local database and output the information to separate JSON-formatted files. Each line outputted to file contains a single actor's:
+ Name
+ Database ID
+ A genre list that includes the movie IDs of movies in each genre that feature the actor
+ A movie list containing the database ID, title, rating, vote count, genre list, and director(s) information for every movie featuring the actor

##### create_movies_json.py
Similar to <code>create_actors_json.py</code>, only outputting movie information instead of actor information. Each line outputted to file contains a single movie's:
+ Title
+ Database ID
+ Rating
+ Vote count
+ Genre list (e.g. ["Comedy", "Drama"])
+ Director(s) information (name and database ID)

##### create_random_movies_json.py
Similar to <code>create_movies_json.py</code>, but instead of iterating through all movies in the database, this script breaks the database ID range into discrete blocks. Each block of IDs then has a randomly chosen subset of IDs selected. The script looks up the subset of IDs instead of every ID in the block range in an attempt to collect a decent random sample of movie information, trading completeness of information for run time.

This script was used to collect a certain percentage of movie information from the database and dump that information into separate files. Then, before compiling all actors' information, the <code>create_actors_json.py</code> can read in a JSON-formatted file of movie information to store in memory. This saves a considerable amount of time compiling actor information by reducing the number of API calls to the database and allowing quick lookups for movie information in memory.

### consolidation_scripts/
Contains scripts to take JSON-formatted files of actors or movies, remove any duplicates from within the file, and output the results in order by ID.
