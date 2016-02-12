# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

Kinematics only -EMG plot from Nexus (no kinetics) + PDF.
L/R sides on separate plots.

@author: Jussi
"""

 
from gp.plot import gaitplotter
import gp.layouts

plotheightratios = [3,2,2,2,2,2]
pdf_prefix = 'Kinematics_EMG_'
maintitleprefix='Kinematics-EMG plot for '

side = 'L'
gplotter = gaitplotter()
gplotter.open_nexus_trial()
plotvars = gp.layouts.kinematics_emg(side)
gplotter.read_trial(plotvars)

trialname = gplotter.trial.trialname
maintitle = maintitleprefix + trialname + ' ('+side+')'
maintitle = maintitle + '\n' + gplotter.get_emg_filter_description()

gplotter.plot_trial(plotheightratios=plotheightratios, maintitle=maintitle)
gplotter.create_pdf(pdf_name=pdf_prefix+trialname+'_'+side+'.pdf')
gplotter.show()


side = 'R'
gplotter = gaitplotter()
gplotter.open_nexus_trial()
plotvars = gp.layouts.kinematics_emg(side)
gplotter.read_trial(plotvars)

trialname = gplotter.trial.trialname
maintitle = maintitleprefix + trialname + ' ('+side+')'
maintitle = maintitle + '\n' + gplotter.get_emg_filter_description()

gplotter.plot_trial(plotheightratios=plotheightratios, maintitle=maintitle)
gplotter.create_pdf(pdf_name=pdf_prefix+trialname+'_'+side+'.pdf')
gplotter.show()



