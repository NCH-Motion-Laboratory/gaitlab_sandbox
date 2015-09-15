# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

single emg plot from c3d

@author: Jussi
"""

from gp.plot import gaitplotter
import gp.layouts

layout = [9,2]
plotvars = gp.layouts.std_emg
trialpath = 'C:/Users/HUS20664877/Desktop/Vicon/vicon_data/test/D0012_VS/2015_6_9_seur_VS/2015_6_9_seur_VS29.c3d'

gplotter = gaitplotter(layout)
gplotter.open_c3d_trial(trialpath)
gplotter.read_trial(plotvars)
maintitle = 'EMG plot for ' + nplotter.trial.trialname + '\n' + nplotter.get_emg_filter_description()
gplotter.plot_trial(maintitle=maintitle)
   
gplotter.show()

