# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

C3D EMG overlay plot. wip

@author: Jussi
"""

from gp.plot import gaitplotter
from gp.getdata import error_exit
import gp.layouts

pdftitlestr = 'EMG_overlay_'
emgcolors = ['black','blue','gray','red']
plotvars = gp.layouts.overlay_emg
MAX_TRIALS = 4

gplotter = gaitplotter()
gplotter.annotate_disconnected = False
maintitle = 'EMG overlay plot '+'('+gplotter.get_emg_filter_description()+')'
ts = gplotter.c3d_trialselector(max_trials=MAX_TRIALS, initialdir='C:/Users/HUS20664877/Desktop/Vicon/vicon_data/test')
chosen = ts.chosen

if len(chosen) > MAX_TRIALS:
    error_exit('Too many trials selected for the overlay plot!')
  
for i,trialpath in enumerate(chosen):
    gplotter.open_c3d_trial(trialpath)
    gplotter.read_trial(plotvars)
    gplotter.plot_trial(maintitle=maintitle,
                        emg_tracecolor=emgcolors[i])
    
gplotter.show()

