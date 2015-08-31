# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

Kinematics-EMG plot from Nexus.

@author: Jussi
"""

 
from gait_plot import gaitplotter
import gaitplotter_plots

layout = [8,3]
plotheightratios = [3,2,2,3,2,2,2,3]
pdf_prefix = 'Kinetics_EMG_'
maintitleprefix='Kinetics-EMG plot for '
nplotter = gaitplotter(layout)

# need to open trial before detecting side
nplotter.open_nexus_trial()
side = nplotter.trial.kinetics_side
plotvars = gaitplotter_plots.kinetics_emg(side)

# choose EMG variables according to side
nplotter.read_trial(plotvars)

trialname = nplotter.trial.trialname
maintitle = maintitleprefix + trialname
maintitle = maintitle + '\n' + nplotter.get_emg_filter_description()

nplotter.plot_trial(plotheightratios=plotheightratios, maintitle=maintitle)
nplotter.create_pdf(pdf_prefix=pdf_prefix)

nplotter.show()


