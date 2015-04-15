# -*- coding: utf-8 -*-
"""
Created on Wed Apr 15 13:56:23 2015

@author: jussi
"""

import csv

with open('ItemInfo.csv') as csvfile:
    csvreader=csv.reader(csvfile)
    for row in csvreader:
        print(', '.join(row))
