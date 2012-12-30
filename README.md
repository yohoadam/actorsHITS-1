## Actor's HITS

Actor's HITS is a Python-based program for determining the best actors of common genres. This program utilizes the IMDbPY API (http://imdbpy.sourceforge.net/) to gather movie information from the Internet Movie Database (http://www.imdb.com). As of this writing (November 2012), IMDb has roughly 280,000 feature films and over 2,000,000 actors/actresses in its database.

Movies in IMDb contain data about the cast list, directors, genres, rating, and number of rating votes by users, among other categories. This program looks up every actor/actress in the database and selected information about every film in which he/she starred. Every actor/actress is then given, using a hubs and authorities algorithm, a weighted score based on the rating for every film genre in which they appear. Each genre is then sorted by these ratings, determining the top-rated actors/actresses of every genre.

## Directories
### algorithm/
Contains scripts for running HITS on some provided corpus of actor data, as well as unit tests for the algorithm.

### crawler/
Contains scripts used to compile movie and actor information from a local PostgreSQL database.

### actor_blocks/
Contains all actor data collected from the database in 100,000 ID blocks. This data includes the extended movie information for every movie in which every actor has appeared. Thus, a considerable amount of redundant movie information is recorded.

### trimmed_actor_blocks/
Similar to <code>actor_blocks</code>, except the dictionary for every actor does not include a <code>'movies'</code> entry for the extended movie information of each movie in which the actor appears. It is expected that the extended movie information is recorded separately so that it may be retrieved using the movie database IDs in the actors' information.
