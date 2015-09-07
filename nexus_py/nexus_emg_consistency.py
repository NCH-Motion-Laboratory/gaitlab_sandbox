# -*- coding: utf-8 -*-
"""
Created on Thu Sep 03 14:54:34 2015

EMG consistency plot from Nexus. Automatically picks trials based on Eclipse
description and defined search strings.

@author: Jussi
"""

from gait_plot import gaitplotter
import gait_getdata
from gait_getdata import get_eclipse_key
import gaitplotter_plots
import glob

def any_substr(str, substrs):
    """ Find whether str contains one of substr (list). """
    if str:
        return any(substr in str for substr in substrs)
    else:
        return None

MAX_TRIALS = 6

if not gait_getdata.nexus_pid():
    gait_getdata.error_exit('Vicon Nexus not running')
    
# get session path from Nexus, find processed trials
vicon = gait_getdata.viconnexus()
trialname_ = vicon.GetTrialName()
sessionpath = trialname_[0]
c3dfiles = glob.glob(sessionpath+'*.c3d')

# Eclipse trial notes/description must contain one of these strings
marks = ['R1','R2','R3','L1','L2','L3']
marked_trials = [c3d for c3d in c3dfiles if any_substr(get_eclipse_key(c3d, 'DESCRIPTION').upper()+' '+get_eclipse_key(c3d, 'NOTES').upper(), marks)]
if len(marked_trials) > MAX_TRIALS:
    gait_getdata.error_exit('Too many marked trials found, how come?')

if not marked_trials:
    gait_getdata.error_exit('Did not find any marked trials in current session directory.')
    
# two extra subplots to accommodate legend
layout = [10,2]
plotvars = gaitplotter_plots.overlay_emg
emgcolors = ['b','g','r','c','m','y','k']

nplotter = gaitplotter(layout)
nplotter.annotate_disconnected = False
maintitle = 'EMG consistency plot '+'('+nplotter.get_emg_filter_description()+')'

for i,trialpath in enumerate(marked_trials):
    nplotter.open_c3d_trial(trialpath)
    nplotter.read_trial(plotvars)
    nplotter.plot_trial(maintitle=maintitle,
                        emg_tracecolor=emgcolors[i])
    
nplotter.show()
nplotter.create_pdf('emg_consistency.pdf')

    