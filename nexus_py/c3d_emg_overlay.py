# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

C3D EMG overlay plot. wip

@author: Jussi
"""

from gait_plot import gaitplotter
import sys
from gait_getdata import error_exit
import gaitplotter_plots

layout = [9,2]
pdftitlestr = 'EMG_overlay_'
emgcolors = ['black','blue','gray','red']
plotvars = gaitplotter_plots.overlay_emg
MAX_TRIALS = 4

nplotter = gaitplotter(layout)
nplotter.annotate_disconnected = False
maintitle = 'EMG overlay plot '+'('+nplotter.get_emg_filter_description()+')'
ts = nplotter.c3d_trialselector(max_trials=MAX_TRIALS, initialdir='C:/Users/HUS20664877/Desktop/Vicon/vicon_data/test')
chosen = ts.chosen


if len(chosen) > MAX_TRIALS:
    error_exit('Too many trials selected for the overlay plot!')
  
for i,trialpath in enumerate(chosen):
    nplotter.open_c3d_trial(trialpath)
    nplotter.read_trial(plotvars)
    nplotter.plot_trial(maintitle=maintitle,
                        emg_tracecolor=emgcolors[i])
    
nplotter.show()

