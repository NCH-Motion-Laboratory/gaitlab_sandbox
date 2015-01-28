# -*- coding: utf-8 -*-
"""
Created on Thu Jan 15 09:49:34 2015

@author: vicon123
"""

from __future__ import print_function

n,m=10,11

# how to print
print('numbers are %d and %d' % (n,m)) # pass as tuple
print('numbers are',n,'and',m)  # multiargument, ' ' default separator
print('numbers are {} and {}'.format(n,m))  # positional formatting
print('numbers are {nval} and {mval}'.format(nval=n,mval=m))  # named arg formatting

# multiline
txt2='''
    n:{n}
    m:{m}'''.format(n=n,m=m)

   
print(txt2)