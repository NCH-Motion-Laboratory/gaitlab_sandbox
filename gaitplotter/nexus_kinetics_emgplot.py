# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

Kinetics-EMG plot from Nexus.

@author: Jussi
"""

 
from gp.plot import gaitplotter
import gp.layouts
from gp.misc import error_exit

plotheightratios = [3,2,2,3,2,2,2,3]
pdf_prefix = 'Kinetics_EMG_'
maintitleprefix='Kinetics-EMG plot for '
gplotter = gaitplotter()

# need to open trial before detecting side
gplotter.open_nexus_trial()
side = gplotter.trial.kinetics_side
if not side:
    error_exit('Forceplate strike not detected, no kinetics available. Check that the subject weight '+
                'is correctly entered and there is a clean forceplate strike.')
    
plotvars = gp.layouts.kinetics_emg(side)

# choose EMG variables according to side
gplotter.read_trial(plotvars)

trialname = gplotter.trial.trialname
maintitle = maintitleprefix + trialname
maintitle = maintitle + '\n' + gplotter.get_emg_filter_description()

gplotter.plot_trial(plotheightratios=plotheightratios, maintitle=maintitle)
gplotter.create_pdf(pdf_prefix=pdf_prefix)

gplotter.show()


