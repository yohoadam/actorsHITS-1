## algorithm/

Contains scripts for running HITS on some provided corpus of actor data. The file <code>sample_hits.json</code> contains a list of eight sample actors that star in various kinds of movies and can be used to demonstrate what the algorithm in <code>hits.py</code> does.

HITS algorithm usage:
    <pre><code>$ python hits.py &lt;actor_info_file.json&gt;</code></pre>

#### algorithm/tests/
Testing scripts for the Hits class implemented in <code>algorithm/</code>.

To run tests:
    <pre><code>$ nosetests -s</code></pre>
