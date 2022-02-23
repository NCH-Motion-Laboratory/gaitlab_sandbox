# -*- coding: utf-8 -*-
"""
Created on Thu Feb 09 11:17:51 2017

@author: hus20664877
"""


import matplotlib.pyplot as plt
import numpy as np

FONTSIZE = 15
LEGEND_FONTSIZE = 12
UPK_LEGEND = 'Ulkopaikkakuntalaisten osuus\n(vuoden 2021 tietoa ei Apotista saatavilla)'

# set global font size
plt.rc('font', size=FONTSIZE)


def autolabel(rects, label_zeros=True):
    """
    Attach a text label above each bar displaying its height
    If label_zeros is False, don't label bars with zero height.
    """
    for rect in rects:
        height = rect.get_height()
        if label_zeros or height != 0:
            plt.text(
                rect.get_x() + rect.get_width() / 2,
                1.01 * height,
                '%d' % int(height),
                ha='center',
                va='bottom',
                fontsize=FONTSIZE-2,
                rotation=90,
            )


# specify input data

# years corresponding to data vectors
yrs = range(2012, 2022)
# optionally, only plot data for certain years
yrs_plot = range(2015, 2022)

# 2020 uudet kategoriat:
#
# yläraaja
# liikelaajuus = kliininen mittaus
# kelkkamittaus
# hengityskaasu

data = dict()  # bars will be plotted in the order they are given here
data['Kävelyanalyysi'] = dict()
data['Kävelyanalyysi']['total'] = [46, 45, 50, 67, 93, 137, 101, 124, 87, 100]
data['Kävelyanalyysi']['ulko'] = [0, 0, 0, 0, 12, 23, 29, 33, 25, 0]

data['Kliiniset mittaukset'] = dict()
data['Kliiniset mittaukset']['total'] = [
    46, 45, 50, 67, 93, 137, 101, 124, 94, 160]
data['Kliiniset mittaukset']['ulko'] = [0, 0, 0, 0, 12, 23, 29, 33, 25, 0]

data['Laitteistetut lihasvoimamittaukset'] = dict()
data['Laitteistetut lihasvoimamittaukset']['total'] = [
    55,
    41,
    47,
    43,
    62,
    60,
    34,
    14,
    23,
    24,
]
data['Laitteistetut lihasvoimamittaukset']['ulko'] = [
    0, 0, 0, 0, 14, 20, 10, 3, 14, 0]

data['Painejakaumamittaukset'] = dict()
data['Painejakaumamittaukset']['total'] = [
    0, 0, 0, 0, 77, 135, 105, 150, 162, 169]
data['Painejakaumamittaukset']['ulko'] = [0, 0, 0, 0, 10, 25, 32, 36, 25, 0]

data['EMG-mittaukset'] = dict()
data['EMG-mittaukset']['total'] = [0, 0, 0, 0, 0, 114, 93, 106, 83, 100]
data['EMG-mittaukset']['ulko'] = [0, 0, 0, 0, 0, 23, 28, 33, 25, 0]

data['Kävelyanalyysin viiteaineisto'] = dict()
data['Kävelyanalyysin viiteaineisto']['total'] = [
    0, 0, 0, 0, 0, 21, 4, 36, 0, 0]
data['Kävelyanalyysin viiteaineisto']['ulko'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

data['Yläraaja'] = dict()
data['Yläraaja']['total'] = [0, 0, 0, 0, 0, 0, 0, 0, 7, 6]
data['Yläraaja']['ulko'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

data['Hengityskaasu'] = dict()
data['Hengityskaasu']['total'] = [0, 0, 0, 0, 0, 0, 0, 0, 7, 4]
data['Hengityskaasu']['ulko'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

data['Kelkkamittaukset'] = dict()
data['Kelkkamittaukset']['total'] = [0, 0, 0, 0, 0, 0, 0, 0, 10, 0]
data['Kelkkamittaukset']['ulko'] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# check length
for var, di in data.items():
    for name, li in di.items():
        if len(li) != len(yrs):
            raise RuntimeError('invalid data length for %s/%s' % (var, name))

# crop data to desired years
# assumes continuous ranges
start_ind, end_ind = yrs.index(yrs_plot[0]), yrs.index(yrs_plot[-1])
for var, di in data.items():
    for name, li in di.items():
        di[name] = li[start_ind:end_ind+1]

for subdata in data.values():
    subdata['total'] = np.array(subdata['total'])
    subdata['ulko'] = np.array(subdata['ulko'])
    subdata['HUS'] = subdata['total'] - subdata['ulko']

fig = plt.figure(figsize=(14, 10))

# compute spacing between bars
n_subdata = len(data)
bar_spacing = 0.1  # min spacing between bar sets
bar_width = (1 - bar_spacing) / n_subdata

# plot all bars
cmap = plt.get_cmap("tab10")
bars = list()
bars_u = list()
for k, (title, subdata) in enumerate(data.items()):
    shift = (k - n_subdata / 2) * bar_width
    b = plt.bar(
        [y + shift for y in yrs_plot], subdata['total'], width=bar_width, color=cmap(k)
    )
    [br.set_edgecolor("black") for br in b]
    bu = plt.bar(
        [y + shift for y in yrs_plot],
        subdata['ulko'],
        width=bar_width,
        color=cmap(k),
        hatch='//',
    )
    [br.set_edgecolor("black") for br in bu]
    bars.append(b)
    bars_u.append(bu)

for b in bars:
    autolabel(b)

for b in bars_u:
    autolabel(b, label_zeros=False)

plt.legend(
    bars + bars_u[:1], list(data.keys()) + [UPK_LEGEND], loc='upper left', fontsize=LEGEND_FONTSIZE
)
plt.ylabel('Potilaita')
plt.xlabel('Vuosi')
# shift the xticklabels a bit
plt.xticks(yrs_plot)
locs, labels = plt.xticks()
locs = [x - 0.25 for x in locs]
plt.xticks(locs, yrs_plot)

this_year = max(yrs_plot)
fn = f'tilastot_{this_year}.png'
fig.set_size_inches(18.5, 10.5)
plt.savefig(fn, dpi=200)
print(f'wrote {fn}')
