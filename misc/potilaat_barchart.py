# -*- coding: utf-8 -*-
"""
Created on Thu Feb 09 11:17:51 2017

@author: hus20664877
"""


import matplotlib.pyplot as plt
import numpy as np
from collections import OrderedDict


def autolabel(rects):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        if height != 0:
            plt.text(rect.get_x() + rect.get_width()/2., 1.01*height,
                     '%d' % int(height), ha='center', va='bottom', fontsize=9)

# specify input data
yrs = range(2012, 2019)

data = OrderedDict()  # bars will be plotted in the order they are given here
data[u'Kävelyanalyysi'] = dict()
data[u'Kävelyanalyysi']['total'] = [46, 45, 50, 67, 93, 137, 101]
data[u'Kävelyanalyysi']['ulko'] = [0, 0, 0, 0, 12, 23, 29]

data[u'Kliiniset mittaukset'] = dict()
data[u'Kliiniset mittaukset']['total'] = [46, 45, 50, 67, 93, 137, 101]
data[u'Kliiniset mittaukset']['ulko'] = [0, 0, 0, 0, 12, 23, 29]

data[u'Isometriset lihasvoimamittaukset'] = dict()
data[u'Isometriset lihasvoimamittaukset']['total'] = [55, 41, 47, 43, 62, 60, 34]
data[u'Isometriset lihasvoimamittaukset']['ulko'] = [0, 0, 0, 0, 14, 20, 10]

data[u'Painejakaumamittaukset'] = dict()
data[u'Painejakaumamittaukset']['total'] = [0, 0, 0, 0, 77, 135, 105]
data[u'Painejakaumamittaukset']['ulko'] = [0, 0, 0, 0, 10, 25, 32]

data[u'EMG-mittaukset'] = dict()
data[u'EMG-mittaukset']['total'] = [0, 0, 0, 0, 0, 114, 93]
data[u'EMG-mittaukset']['ulko'] = [0, 0, 0, 0, 0, 23, 28]

data[u'Kävelyanalyysin viiteaineisto'] = dict()
data[u'Kävelyanalyysin viiteaineisto']['total'] = [0, 0, 0, 0, 0, 21, 4]
data[u'Kävelyanalyysin viiteaineisto']['ulko'] = [0, 0, 0, 0, 0, 0, 0]

assert all(len(yrs) == len(li) for di in data.values() for li in di.values())

for subdata in data.values():
    subdata['total'] = np.array(subdata['total'])
    subdata['ulko'] = np.array(subdata['ulko'])
    subdata['HUS'] = subdata['total'] - subdata['ulko']

fig = plt.figure(figsize=(14, 10))

# compute spacing between bars
n_subdata = len(data)
bar_spacing = .1  # min spacing between bar sets
bar_width = (1 - bar_spacing) / n_subdata

# plot all bars
cmap = plt.get_cmap("tab10")
bars = list()
bars_u = list()
for k, (title, subdata) in enumerate(data.items()):
    shift = (k - n_subdata/2) * bar_width
    b = plt.bar([y + shift for y in yrs], subdata['total'],
                width=bar_width, color=cmap(k))
    [br.set_edgecolor("black") for br in b]
    bu = plt.bar([y + shift for y in yrs], subdata['ulko'],
                 width=bar_width, color=cmap(k), hatch='//')
    [br.set_edgecolor("black") for br in bu]
    bars.append(b)
    bars_u.append(bu)

for b in bars + bars_u:
    autolabel(b)

plt.legend(bars+bars_u[:1], list(data.keys()) + ['Ulkopaikkakuntalaisia'], loc='upper left')
plt.ylabel('Potilaita')
plt.xlabel('Vuosi')

fig.set_size_inches(18.5, 10.5)
plt.savefig('tilastot_2019.png', dpi=200)



