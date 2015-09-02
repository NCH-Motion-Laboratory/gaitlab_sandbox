# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

Muscle length plot.

@author: Jussi
"""


 
from gait_plot import gaitplotter
import gaitplotter_plots

layout = [3,3]
maintitleprefix='Muscle length plot for '
pdftitlestr='muscle_length_'

nplotter = gaitplotter(layout)
plotvars = gaitplotter_plots.std_musclelen
nplotter.open_nexus_trial()
nplotter.read_trial(plotvars)
trialname = nplotter.trial.trialname
maintitle = maintitleprefix + trialname
maintitle = maintitle + '\n' + nplotter.get_emg_filter_description()
nplotter.plot_trial(maintitle=maintitle)
nplotter.create_pdf(pdf_prefix=pdftitlestr)

nplotter.show()


