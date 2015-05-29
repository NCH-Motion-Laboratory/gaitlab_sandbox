# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

Kinematics-EMG plot from Nexus (no kinetics)

@author: Jussi
"""

 
from nexus_plot import nexus_plotter

layout = [6,3]
plotheightratios = [3,2,2,2,2,2]
pdf_prefix = 'Kinematics_EMG_'
maintitleprefix='Kinematics-EMG plot for '

nplotter = nexus_plotter(layout)

# need to open trial before detecting side
nplotter.open_trial(nexusvars=None)
side = nplotter.side
# choose EMG variables according to side
plotvars = ['HipAnglesX','KneeAnglesX','AnkleAnglesX',
            side+'Ham', side+'Rec', side+'TibA',
            side+'Glut',side+'Vas',side+'Per',
            side+'Rec',side+'Ham',side+'Gas',
            None,side+'Glut',side+'Sol',
            None,side+'Gas',None]

nplotter.open_trial(nexusvars=plotvars)

trialname = nplotter.trialname
maintitle = maintitleprefix + trialname
maintitle = maintitle + '\n' + nplotter.get_emg_filter_description()

nplotter.plot_trial(plotheightratios=plotheightratios, maintitle=maintitle)
nplotter.create_pdf(pdf_prefix=pdf_prefix)

nplotter.show()


