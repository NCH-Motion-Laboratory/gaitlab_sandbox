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

side = 'L'
nplotter = gaitplotter(layout)
nplotter.open_nexus_trial()
plotvars = gaitplotter_plots.kinematics_emg(side)
nplotter.read_trial(plotvars)

trialname = nplotter.trial.trialname
maintitle = maintitleprefix + trialname + ' ('+side+')'
maintitle = maintitle + '\n' + nplotter.get_emg_filter_description()

nplotter.plot_trial(plotheightratios=plotheightratios, maintitle=maintitle)
nplotter.create_pdf(pdf_prefix=pdf_prefix)
nplotter.show()


side = 'R'
nplotter = gaitplotter(layout)
nplotter.open_nexus_trial()
plotvars = gaitplotter_plots.kinematics_emg(side)
nplotter.read_trial(plotvars)

trialname = nplotter.trial.trialname
maintitle = maintitleprefix + trialname + ' ('+side+')'
maintitle = maintitle + '\n' + nplotter.get_emg_filter_description()

nplotter.plot_trial(plotheightratios=plotheightratios, maintitle=maintitle)
nplotter.create_pdf(pdf_prefix=pdf_prefix)
nplotter.show()



