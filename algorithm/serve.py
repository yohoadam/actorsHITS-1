#!/usr/bin/env python
# web server for actor search
# You should not need to edit this file.

import time
import sys
import bottle
import hits
import utils
from settings import settings

_hits= None

@bottle.route('/search')
def search(name='World'):
    global _searcher
    query = bottle.request.query.q
    start_time = time.time()
    actors_list = _hits.query_hits(query)
    end_time = time.time()

    return dict(
            actors = actors_list,
            count = len(actors_list),
            time = end_time - start_time,
            )


@bottle.route('/genres')
def get_genres():
    return _hits.genres


@bottle.route('/')
def index():
    return bottle.static_file('index.html', root='static')


@bottle.route('/favicon.ico')
def favicon():
    return bottle.static_file('favicon.ico', root='static')


@bottle.route('/static/<filename:path>')
def server_static(filename):
    return bottle.static_file(filename, root='static')


if __name__=="__main__":
    if len(sys.argv) < 4:
        print '\nMissing input argument!\n'
        print '\tusage:', sys.argv[0], '<genre_list.json> <movie_info_list.json> <actor_list.json>\n'
        quit()

    _hits=hits.HITS()
    _hits_calculator = _hits.initialize_for_query(sys.argv[1], sys.argv[2], sys.argv[3])
    bottle.run(host=settings['http_host'],
               port=settings['http_port'],
               reloader=False)
