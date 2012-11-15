'''
Created on Nov 15, 2012

'''
import utils
import unittest


class HITS_TEST(unittest.TestCase):
    def setUp(self):
        pass

    


if __name__=="__main__":
    print 'start reading json file for each record'
    records=utils.read_records()
    print 'done reading'