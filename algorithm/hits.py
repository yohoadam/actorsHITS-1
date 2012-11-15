'''
Created on Nov 15, 2012

@author: 
'''


class HITS(object):
    def __init__(self):
        pass    
    
    def index_actors(self,actors_info):        
        for actor in list(actors_info)[0]:
            print "%s %s genres covered: %s"%(actor.get('id'),actor.get('name'),' '.join(actor.get('genre_list')))
            for movies in actor.get('movies',[]):
                print " -----> %s %s %d %s"%(movies.get('title'),movies.get('id'),movies.get('rating'),' '.join(movies.get('genres')))
                           
    def core_algorithm(self):
        pass
    