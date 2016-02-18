from __future__ import print_function
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 20 09:16:10 2015

@author: vicon123
"""

def allints(n):
    for i in range(n):
        yield i
        
        
a = allints(100)
