# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

Kinematics-EMG plot from Nexus.

@author: Jussi
"""

 
from gp.plot import gaitplotter
import gp.layouts

layout = [8,3]
plotheightratios = [3,2,2,3,2,2,2,3]
pdf_prefix = 'Kinetics_EMG_'
maintitleprefix='Kinetics-EMG plot for '
gplotter = gaitplotter(layout)

# need to open trial before detecting side
gplotter.open_nexus_trial()
side = gplotter.trial.kinetics_side
plotvars = gp.layouts.kinetics_emg(side)

# choose EMG variables according to side
gplotter.read_trial(plotvars)

trialname = gplotter.trial.trialname
maintitle = maintitleprefix + trialname
maintitle = maintitle + '\n' + gplotter.get_emg_filter_description()

gplotter.plot_trial(plotheightratios=plotheightratios, maintitle=maintitle)
gplotter.create_pdf(pdf_prefix=pdf_prefix)

gplotter.show()


