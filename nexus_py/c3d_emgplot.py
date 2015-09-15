# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

single emg plot from c3d

@author: Jussi
"""

from gait_plot import gaitplotter
import gaitplotter_plots

layout = [9,2]
plotvars = gaitplotter_plots.std_emg
trialpath = 'C:/Users/HUS20664877/Desktop/Vicon/vicon_data/test/D0012_VS/2015_6_9_seur_VS/2015_6_9_seur_VS29.c3d'

nplotter = gaitplotter(layout)
nplotter.open_c3d_trial(trialpath)
nplotter.read_trial(plotvars)
maintitle = 'EMG plot for ' + nplotter.trial.trialname + '\n' + nplotter.get_emg_filter_description()
nplotter.plot_trial(maintitle=maintitle)
   
nplotter.show()

