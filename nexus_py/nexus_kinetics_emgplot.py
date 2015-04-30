# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

Kinematics-EMG plot from Nexus.

@author: Jussi
"""

from nexus_plot import nexus_plotter
import matplotlib.pyplot as plt

layout = [8,3]
plotvars = ['HipAnglesX','KneeAnglesX','AnkleAnglesX',
            'XHam', 'XRec', 'XTibA',
            'XGlut','XVas','XPer',
            'HipMomentX','KneeMomentX','AnkleMomentX',
            'XRec','XHam','XGas',
            None,'XGlut','XSol',
            None,'XGas',None,
            'HipPowerZ','KneePowerZ','AnklePowerZ']

plotheightratios = [3,2,2,3,2,2,2,3]
maintitlestr = 'Kinetics-EMG plot for '
makepdf = True
pdftitlestr = 'Kinetics_EMG_'

nplotter = nexus_plotter(layout, plotvars)
nplotter.open_trial()
nplotter.plot_trial(plotheightratios=plotheightratios, maintitlestr=maintitlestr, 
           makepdf=False, pdftitlestr=pdftitlestr, onesided_kinematics=True)

nplotter.tracecolor_l = 'blue'

nplotter.open_trial('C:\\Users\\HUS20664877\\Desktop\\Vicon\\vicon_data\\test\\D0001AV\\2015_4_23_seur_AV\\2015_4_23_seur_AV19')
nplotter.plot_trial(plotheightratios=plotheightratios, maintitlestr=maintitlestr, 
           makepdf=makepdf, pdftitlestr=pdftitlestr, onesided_kinematics=True)


plt.show()