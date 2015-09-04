# -*- coding: utf-8 -*-
"""
Created on Thu Sep 03 14:54:34 2015

EMG consistency plot from Nexus. Automatically picks trials based on Eclipse
description.

@author: Jussi
"""

from gait_plot import gaitplotter
import gait_getdata
import gaitplotter_plots
import glob

def is_marked_trial(desc):
    """ Find whether trial description has one of the defined markings. """
    marks = ['R1','R2','R3','L1','L2','L3']
    return any(mark in desc.upper() for mark in marks)

# get session path from Nexus
vicon = gait_getdata.viconnexus()
trialname_ = vicon.GetTrialName()
sessionpath = trialname_[0]
c3dfiles = glob.glob(sessionpath+'*.c3d')
marked_trials = [c3d for c3d in c3dfiles if is_marked_trial(gait_getdata.get_eclipse_description(c3d))]
# two extra subplots to accommodate legend
layout = [10,2]
plotvars = gaitplotter_plots.overlay_emg
emgcolors = ['b','g','r','c','m','y','k']

nplotter = gaitplotter(layout)
nplotter.annotate_disconnected = False
maintitle = 'EMG consistency plot' + '\n' + nplotter.get_emg_filter_description()

for i,trialpath in enumerate(marked_trials):
    nplotter.open_c3d_trial(trialpath)
    nplotter.read_trial(plotvars)
    nplotter.plot_trial(maintitle=maintitle,
                        emg_tracecolor=emgcolors[i])
    nplotter.show()

    






