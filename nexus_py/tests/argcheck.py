# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 15:23:37 2015

@author: HUS20664877
"""

import sys


def RetTup():
    return 1,2

class oma:
    def funfun(self):
        return 1
    def __init__(self):
        a = self.funfun()
        print a
        
        
        


    


class NotProcessed(Exception):
    def __init__(self, msg):
        self.msg = msg


def funex():
    raise NotProcessed('xxx')

def foo():
    funex()
    

def bar():
    try:
        foo()
    except NotProcessed:
        print('Not Processed caught!')
        
    
 
bar() 
sys.exit()



class NotProcessed(Exception):
    def __init__(self, msg):
        self.msg = msg
        
try:
    raise NotProcessed('jotain')
except NotProcessed as np:
    print np.msg
    


class ChannelNotFound(Exception):
    def __init__(self, chname):
        self.chname = chname
    def __str__(self):
        return repr(self.chname)

raise ChannelNotFound()
        
try:
    raise ChannelNotFound('LTib')
except ChannelNotFound as c:
    print 'Cannot find channel:', c.chname
    




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

