## data/

Contains all actor data collected from the database. Data is split into blocks of ID ranges of 100,000. Each individual JSON file should contain a little less than half that number in actual actor information.

Actor information is in the form (all contained on one line):
&lt;pre&gt;&lt;code&gt;
{
  "movies": {
    &lt;movie_id*&gt; : {
	  "rating": &lt;rating&gt;,
	  "genres": [&lt;genre_1&gt;, &lt;genre_2&gt;, ...],
	  "title": &lt;movie_title&gt;,
	  "votes": &lt;votes&gt;,
	  "director": { &lt;director_1_id&gt;: &lt;director_1_name&gt;, ...},
	  "id": &lt;movie_id&gt;
	}
  },
  "genre_list": {&lt;genre_1&gt;: [genre_movie_1_id, ...], ...},
  "id": &lt;actor_id&gt;,
  "name": &lt;actor_name&gt;
}
&lt;/code&gt;&lt;/pre&gt;

where the values are defined as follows:

&lt;pre&gt;&lt;code&gt;

&lt;movie_id*&gt;          Database ID of the movie (string)
&lt;movie_id&gt;           Database ID of the movie (integer)
&lt;rating&gt;             Rating of the movie (float)
&lt;genre_i&gt;            Genre name (string) (e.g. "Drama", "Action")
&lt;movie_title&gt;        Movie title (string) (e.g. "The Godfather (1972)")
&lt;votes&gt;              Number of votes for a movie (integer)
&lt;director_i_id&gt;      Database ID of the director (integer)
&lt;director_i_name&gt;    Name of the director (string)
&lt;genre_movie_i_id&gt;   Database ID of a movie in this genre (integer) (Identical to &lt;movie_id&gt;)
&lt;actor_id&gt;           Database ID of an actor (integer)
&lt;actor_name&gt;         Name of an actor (string)

&lt;/code&gt;&lt;/pre&gt;
