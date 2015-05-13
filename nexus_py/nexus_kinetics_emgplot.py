# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

Kinematics-EMG plot from Nexus.

@author: Jussi
"""


from nexus_plot import nexus_plotter

layout = [8,3]
plotheightratios = [3,2,2,3,2,2,2,3]
pdf_prefix = 'Kinetics_EMG_'

nplotter = nexus_plotter(layout)

# need to open trial before detecting side
nplotter.open_trial(nexusvars=None)
side = nplotter.side
# choose EMG variables according to side
plotvars = ['HipAnglesX','KneeAnglesX','AnkleAnglesX',
            side+'Ham', side+'Rec', side+'TibA',
            side+'Glut',side+'Vas',side+'Per',
            'HipMomentX','KneeMomentX','AnkleMomentX',
            side+'Rec',side+'Ham',side+'Gas',
            None,side+'Glut',side+'Sol',
            None,side+'Gas',None,
            'HipPowerZ','KneePowerZ','AnklePowerZ']

nplotter.open_trial(nexusvars=plotvars)
nplotter.plot_trial(plotheightratios=plotheightratios, maintitleprefix='Kinetics-EMG plot for ')

nplotter.show()
nplotter.create_pdf(pdf_prefix=pdf_prefix)

