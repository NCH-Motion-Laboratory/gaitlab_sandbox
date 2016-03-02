# -*- coding: utf-8 -*-
"""
Created on Thu Feb 04 10:44:07 2016

@author: hus20664877
"""

from __future__ import print_function
import string
import sys

di = {'a': 1, 'b': 2, 'c': 3, 'x': 4, 'y': None}

tli = ['JOTAIN', 'a: {a} b: {b}', 'x: {x}', 'b: {b}', 'c: {c}', 'y: {y}']

s = tli[1]


def get_field(s):
    fi = string.Formatter()
    pit = fi.parse(s)  # parser iterator
    for items in pit:
        yield items[1]
    
def format_item(s, di):
    flds = list(get_field(s))
    if not any(flds):
        return s
    else:
        if any([di[fld] for fld in flds]):
            return s.format(**di)            

def noval():
    pass

for fld in get_field(s):
    print(fld)
    
sys.exit()
    
for s,i in enumerate(tli):
    print(i)
    for fi in get_field(s):
        print(fi)

sys.exit()




""" Conditional formatter for a list of string items:
Format only items that have their fields defined in di. (TODO: some fields)
Assumes one field per item (only looks at the first field).
Items whose fields are not present are excluded. 
Returns a new list. """
def cond_format(items, di):
    li = []
    for st in items:
        pai = fi.parse(st)  # parsing iterator that returns tuples of strings, fields etc.
        fld = pai.next()[1]
        if fld:
            if di[fld]:
                li.append(st.format(**di))
        else:
            li.append(st)
    return li

print(cond_format(tli, di))
    
    





""" Conditional formatter for iterable of strings:
Format only strings that have their fields defined in di.
Assumes one field per item (only looks at the first field).
Items whose fields are not present are excluded. 
Format using dict di. """
def cond_format(items, di):
    fi = string.Formatter()
    for st in items:
        pai = fi.parse(st)  # parsing iterator that returns tuples of strings, fields etc.
        for fld in pai:
            fld = pai.next()[1]
            if fld:
                if di[fld]:
                    yield st.format(**di)
            else:
                yield st

cfo = cond_format(tli, di)    

for li in cfo:
    print(li)
    
    