# -*- coding: utf-8 -*-
"""
Created on Thu Feb 09 11:17:51 2017

@author: hus20664877
"""


import matplotlib.pyplot as plt
import operator
import numpy as np

bar_width = .4
dbar = .0

yr = [2012,2013,2014,2015,2016,2017]

voimat = [55,41,47,43,48]
kavely = [46,45,50,67,81,114]
paine = []

nort = [9,8,8,5,7,5,6,8,7,10,12]

plt.figure(figsize=(14,10))

b1 = plt.bar([y-bar_width for y in yr], spast, width=bar_width, color='green')
b2 = plt.bar([y+dbar for y in yr], nort, width=bar_width, color='r')

plt.ylabel('Kokouksia')
plt.xlabel('Vuosi')
plt.xlim([2005, 2017])
plt.ylim([0, 50])
tickx = np.arange(2005, 2018)
ticktxt = [str(x) for x in tickx]
ticktxt[0] = ''
ticktxt[-1] = ''
plt.xticks(tickx, ticktxt)
plt.legend((b1[0], b2[0]), (u'Spast. kokouksia',
                            u'Neuro-ortop. kokouksia',
                            ),
            fontsize=11, loc='upper left')

def autolabel(rects):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width()/2., 1.01*height,
                '%d' % int(height),
                ha='center', va='bottom', fontsize=9)


def autolabel_ctr(rects):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width()/2., rect.get_y() + .5*height-.5,
                '%d' % int(height),
                ha='center', va='center', fontsize=9)


                
autolabel(b1)  # total
autolabel(b2)  # total

