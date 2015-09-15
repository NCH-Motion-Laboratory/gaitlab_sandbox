# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:25:38 2015

EMG plot from Nexus.

@author: Jussi
"""

from gp.plot import gaitplotter
import gp.layouts

layout = [8,2]
maintitleprefix = 'EMG plot for '
pdftitlestr = 'EMG_'

gplotter = gaitplotter(layout)
plotvars = gp.layouts.std_emg
gplotter.open_nexus_trial()
gplotter.read_trial(plotvars)
trialname = gplotter.trial.trialname
maintitle = maintitleprefix + trialname
maintitle = maintitle + '\n' + gplotter.get_emg_filter_description()
gplotter.plot_trial(maintitle=maintitle)
gplotter.create_pdf(pdf_prefix=pdftitlestr)

gplotter.show()



