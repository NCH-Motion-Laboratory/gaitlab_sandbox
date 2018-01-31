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

yr = [2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016]

spast = [45,104,102,101,80,97,133,106,92,118,119,109]

nort = [17,30,30,20,13,20,22,22,24,23,33,29]

nort_ulkop = [4,7,8,7,6,9,8,7,6,9,21,14]

nort_hki = map(operator.sub, nort, nort_ulkop)

plt.figure(figsize=(14,10))

b1 = plt.bar([y-bar_width for y in yr], spast, width=bar_width, color='green')

b2 = plt.bar([y+dbar for y in yr], nort, width=bar_width, color='r')
b3 = plt.bar([y+dbar for y in yr], nort_ulkop, width=bar_width, bottom=nort_hki, color='y')
b4 = plt.bar([y+dbar for y in yr], nort_hki, width=bar_width, color='r')

plt.ylabel('Potilaita')
plt.xlabel('Vuosi')
plt.xlim([2004.5, 2016.5])
plt.ylim([0, 160])
tickx = np.arange(2004, 2018)
ticktxt = [str(x) for x in tickx]
ticktxt[0] = ''
ticktxt[-1] = ''
plt.xticks(tickx, ticktxt)
plt.legend((b1[0], b2[0], b3[0]), (u'Spast. kokouksissa käsiteltyjä potilaita, HUS-alue ja ulkopaikkakuntalaiset',
                                   u'Neuro-ortop. kokouksissa käsiteltyjä potilaita, HUS-alue',
                                   u'Neuro-ortop. kokouksissa käsiteltyjä potilaita, ulkopaikkakuntalaiset'),
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
autolabel_ctr(b3)
autolabel_ctr(b4)

