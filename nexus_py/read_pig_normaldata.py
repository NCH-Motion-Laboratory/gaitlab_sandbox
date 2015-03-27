# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 16:18:45 2015

@author: jussi
"""

"""
read data from normal.gcd
if line starts with !, read variable name immediately after !
numeric data will follow
"""

fn = 'C:/Users/HUS20664877/Desktop/projects/llinna/nexus_py/normal.gcd'

f = open(fn, 'r')
lines = f.readlines()
f.close()

pig_normaldata = {}
for li in lines:
    if li[0] == '!':  # it's a variable name
        thisvar = li[1:li.find(' ')]  # set dict key
        pig_normaldata[thisvar] = list()
    elif li[0].isdigit() or li[0] == '-':  # it's a number, so read into list
        pig_normaldata[thisvar].append([float(x) for x in li.split()])

    