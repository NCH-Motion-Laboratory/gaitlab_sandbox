# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

Kinematics only -EMG plot from Nexus (no kinetics) + PDF.
L/R sides on separate plots.

@author: Jussi
"""

 
from gait_plot import gaitplotter
import gaitplotter_plots

layout = [6,3]
plotheightratios = [3,2,2,2,2,2]
pdf_prefix = 'Kinematics_EMG_'
maintitleprefix='Kinematics-EMG plot for '

nplotter = gaitplotter(layout)
# need to open trial before detecting side
nplotter.open_nexus_trial()
side = nplotter.trial.kinetics
# choose EMG variables according to side
plotvars = gaitplotter_plots.kinetics_emg(side)

nplotter.open_nexus_trial(nexusvars=plotvars)

trialname = nplotter.trialname
maintitle = maintitleprefix + trialname
maintitle = maintitle + '\n' + nplotter.get_emg_filter_description()

nplotter.plot_trial(plotheightratios=plotheightratios, maintitle=maintitle)
nplotter.create_pdf(pdf_prefix=pdf_prefix)

nplotter.show()


