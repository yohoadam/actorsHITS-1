## data/

Contains all actor data collected from the database. Data is split into blocks of ID ranges of 100,000. Each individual JSON file should contain a little less than half that number in actual actor information.

Actor information is in the form (all contained on one line):
<pre><code>
{
  "genre_list": {&lt;genre_1&gt;: [genre_movie_1_id, ...], ...},
  "id": &lt;actor_id&gt;,
  "name": &lt;actor_name&gt;
}
</code></pre>

where the values are defined as follows:

<pre><code>&lt;genre_i&gt;            Genre name (string) (e.g. "Drama", "Action")
&lt;genre_movie_i_id&gt;   Database ID of a movie in this genre (integer)
&lt;actor_id&gt;           Database ID of an actor (integer)
&lt;actor_name&gt;         Name of an actor (string)
</code></pre>
