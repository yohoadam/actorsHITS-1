'''
Created on Nov 15',' 2012
@author: Ananta Uprety

dumps  a list of dictionaries into a json file in this format:
{ "id":20000,
  "name":"Tom Cruise",
  "movies":[ {"id":100, "title":"Mission Impossible", "rating":7, "genres":["Action", "Drama"]},
             {"id":200, "title":"War of the Worlds", "rating":7, "genres":["Action", "Drama", "Sci-Fi"]}
  ],
  "genre_list":["Action", "Drama", "Sci-Fi"]
}


'''


from imdb import IMDb
from sets import Set
import json

ia=IMDb()

'''
action list from wiki :
http://en.wikipedia.org/wiki/List_of_action_film_actors
'''
'''
action_actors=['Angelina Jolie','Arnold Schwarzenegger','Antonio Banderas','Ace Vergel','Ben Affleck','Bong Revilla','Brent Huff','Bruce Lee','Bruce Willis',
               'Charles Bronson','Cesar Montano','Chow Yun-fat','Christian Bale','Chuck Norris','Clint Eastwood','Clive Owen','Cynthia Rothrock','Daniel Craig',
               'Dolph Lundgren','Donnie Yen','Eddie Garcia','Fernando Poe Jr','Jackie Chan','Harrison Ford','Hugh Jackman','Rutger Hauer','Jean-Claude Van Damme',
               'Jean Reno','Jason Statham','Jessica Biel','Jet Li','Joseph Estrada','John Wayne','Kane Kosugi','Keanu Reeves','Kurt Russell','Lee Marvin','Lorenzo Lamas',
               'Lucy Liu','Mel Gibson','Michael Dudikoff','Michelle Yeoh','Milla Jovovich','Monsour del Rosario',
               'Sammo Hung','Sean Connery','Shia LaBeouf','Sigourney Weaver','Steve McQueen','Steven Seagal','Sylvester Stallone','The Rock','Tom Cruise',
               'Tony Jaa','Vin Diesel','Wesley Snipes','Will Smith','Yuen Biao']

'''
action_actors= ['Angelina Jolie','Antonio Banderas']

print len(action_actors)
all_actor_info=[]
for actor in action_actors:
    print actor
    actor_info=ia.search_person(actor)
    print actor_info
    if len(actor_info) > 0:
        actor_id=actor_info[0].getID()
        print actor_id
        person=ia.get_person(actor_id)     
        acted_list = person.get('actor') or person.get('actress')
        genre_set=Set()
        movie_info={}
        movies=[]
        if acted_list:
            print acted_list
            for movie in acted_list[:2]:
                id=movie.getID()
                updated_info=ia.get_movie(id)
                title=updated_info.get('title')
                '''
                if a rating cannot be found I think giving an average rating will not penalize anyone
                we can always change this
                '''
                rating=updated_info.get('rating',5)             
                genres=updated_info.get('genres',[])   
                print "%s %s %d %s"%(id,title,rating,' '.join(genres))
                movie_info={'id':id,'title':title,'rating':rating,'genres':genres}
                movies.append(movie_info)
                genre_set|=Set(genres)
        print genre_set        
        actor_dict={'id':actor_id,'name':person['name'],'movies':movies,'genre_list':list(genre_set)}
        all_actor_info.append(actor_dict)
    
    s=json.dumps(all_actor_info)
    f = open("actors_tiny.json", 'w+')
    f.write(s + "\n")
    f.close() 
   
       
        
