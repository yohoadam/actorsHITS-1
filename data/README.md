## data/

Contains all actor data collected from the database. Data is split into blocks of ID ranges of 100,000. Each individual JSON file should contain a little less than half that number in actual actor information.

Actor information is in the form:
<pre><code>
{
  "movies": {
    <movie_id*> : {
	  "rating": <rating>,
	  "genres": [<genre_1>, <genre_2>, ...],
	  "title": <movie_title>,
	  "votes": <votes>,
	  "director": { <director_1_id>: <director_1_name>, ...},
	  "id": <movie_id>
	}
  },
  "genre_list": {<genre_1>: [genre_movie_1_id, ...], ...},
  "id": <actor_id>,
  "name": <actor_name>
}
</code></pre>

where the values are defined as follows:

<pre><code>

<movie_id*>          Database ID of the movie (string)
<movie_id>           Database ID of the movie (integer)
<rating>             Rating of the movie (float)
<genre_i>            Genre name (string) (e.g. "Drama", "Action")
<movie_title>        Movie title (string) (e.g. "The Godfather (1972)")
<votes>              Number of votes for a movie (integer)
<director_i_id>      Database ID of the director (integer)
<director_i_name>    Name of the director (string)
<genre_movie_i_id>   Database ID of a movie in this genre (integer) (Identical to <movie_id>)
<actor_id>           Database ID of an actor (integer)
<actor_name>         Name of an actor (string)

</code></pre>
