# -*- coding: utf-8 -*-
"""
Created on Thu Sep 03 14:54:34 2015

EMG consistency plot from Nexus. Automatically picks trials based on Eclipse
description.

@author: Jussi
"""

from gait_plot import gaitplotter
import gait_getdata
from gait_getdata import get_eclipse_key
import gaitplotter_plots
import glob

def any_substr(str, substrs):
    """ Find whether str.upper() contains one of substr (list). """
    if str:
        return any(substr in str.upper() for substr in substrs)
    else:
        return None

# get session path from Nexus
vicon = gait_getdata.viconnexus()
trialname_ = vicon.GetTrialName()
sessionpath = trialname_[0]
c3dfiles = glob.glob(sessionpath+'*.c3d')
marks = ['R1','R3','L1','L3']
marked_trials = [c3d for c3d in c3dfiles if any_substr(get_eclipse_key(c3d, 'DESCRIPTION')+get_eclipse_key(c3d, 'NOTES'), marks)]
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

    






#C:/Users/HUS20664877/Desktop/Vicon/vicon_data/test/D0012_VS/2015_6_9_seur_VS/2015_6_9_seur_VS07.c3d