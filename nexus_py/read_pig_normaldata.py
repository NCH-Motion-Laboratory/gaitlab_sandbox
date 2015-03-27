# -*- coding: utf-8 -*-
"""
Created on Fri Mar 27 16:18:45 2015

@author: jussi
"""

"""
read normal.gcd
if line starts with !, read variable name immediately after
read lines as long values are numeric
append numbers into lists
"""

fn = 'C:/Users/HUS20664877/Desktop/projects/llinna/nexus_py/normal.gcd'

f = open(fn, 'r')
lines = f.readlines()
f.close()

vardict = {}
for li in lines:
    if li[0] == '!':  # it's a variable name
        thisvar = li[1:li.find(' ')]  # set dict key
        vardict[thisvar] = list()
    elif li[0].isdigit():  # it's a number, so read into list
        vardict[thisvar].append([float(x) for x in li.split()])


        
        
        
    