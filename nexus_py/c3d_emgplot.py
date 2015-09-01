# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

single emg plot from c3d

@author: Jussi
"""

from gait_plot import gaitplotter
import sys
from gait_getdata import error_exit
import gaitplotter_plots

layout = [9,2]
pdftitlestr = 'EMG_overlay_'

plotvars = gaitplotter_plots.std_emg
trialpath = 'C:/Users/HUS20664877/Desktop/Vicon/vicon_data/test/D0012_VS/2015_6_9_seur_VS/2015_6_9_seur_VS33.c3d'
nplotter = gaitplotter(layout)
nplotter.open_c3d_trial(trialpath)
trialname = nplotter.trial.trialname
maintitle = 'EMG plot for ' + trialname + '\n' + nplotter.get_emg_filter_description()
nplotter.read_trial(plotvars)
nplotter.plot_trial(maintitle=maintitle,
                    emg_tracecolor=emgcolors[i])

   
nplotter.show()
#nplotter.create_pdf(pdf_name='overlay.pdf')

