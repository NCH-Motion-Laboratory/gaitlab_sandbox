# -*- coding: utf-8 -*-
"""
Created on Thu Feb 04 10:44:07 2016

@author: hus20664877
"""

from __future__ import print_function
import string
import sys

di = {'a': 1, 'b': 2, 'c': 3, 'x': 4, 'y': 'Ei'}

tli = ['JOTAIN\n', 'a: {a} b: {b} ', 'x: {x} ', 'b: {b} ', 'c: {c} ', 'y: {y} ']


rep = u"""
RAPORTIN TESTAUSTA

NUMEROITA: #a: {a}# b: {b}#

X ja Y: #x: {x}# y: {y}#
"""


def get_field(s):
    """ Return all fields in a format string. """
    fi = string.Formatter()
    pit = fi.parse(s)  # returns parser generator
    for items in pit:
        if items[1]:
            yield items[1]  # = the field
    
def cond_format(s, di, empty=None):
    """ Conditionally format string s using dict di: if all field values
    equal the 'empty' value, return empty string. """
    flds = list(get_field(s))
    if not flds or any([di[fld] != empty for fld in flds]):
        return s.format(**di)
    else:
        return ''

outs = ''.join([cond_format(s, di, 'Ei') for s in rep.split('#')])

print(outs)


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
    
    