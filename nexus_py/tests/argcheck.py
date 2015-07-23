# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 15:23:37 2015

@author: HUS20664877
"""


class give():

    def __init__(self):
        pass
    
    def do(self):
        print('doing')
        
g1 = give()
give.do(g1)

def fun(val):
    print(val+1)    
    
fun(1)

fo1 = fun

fo1(1)


vara = 1
fo2 = lambda: fun(vara)


vara = 7
fo2()

