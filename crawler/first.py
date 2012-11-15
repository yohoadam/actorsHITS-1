'''
Created on Sep 23, 2012

@author: abeqasim
'''
from imdb import IMDb

ia=IMDb()
'''
the_matrix = ia.get_movie('0133093')
print the_matrix['director']
0948470
'''
id=500000

matrix=None
while True:
    try:
        matrix=ia.get_movie(id)
        if matrix['title']!='':
            print matrix['title'] 
            print matrix.getID()
            print matrix['rating']
            
            print matrix['genres']  
            director= matrix['director'][0]
            print director['name']
            print director.getID()            
            print id
            id+=1
            break
    except:
        id+=1
        pass
#person=ia.get_person()
'''
for person in ia.search_person('Mel Gibson'):
    print person.personID, person['name']
    
print "hello world %d" % 125
'''


