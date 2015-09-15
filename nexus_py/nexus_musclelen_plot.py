# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

Muscle length plot.

@author: Jussi
"""


 
from gp.plot import gaitplotter
import gp.layouts

layout = [3,3]
maintitleprefix='Muscle length plot for '
pdftitlestr='muscle_length_'

gplotter = gaitplotter(layout)
plotvars = gp.layouts.std_musclelen
gplotter.open_nexus_trial()
gplotter.read_trial(plotvars)
trialname = gplotter.trial.trialname
maintitle = maintitleprefix + trialname
maintitle = maintitle + '\n' + gplotter.get_emg_filter_description()
gplotter.plot_trial(maintitle=maintitle)
gplotter.create_pdf(pdf_prefix=pdftitlestr)

gplotter.show()


