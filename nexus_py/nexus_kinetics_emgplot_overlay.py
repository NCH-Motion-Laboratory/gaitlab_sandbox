# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

Kinematics-EMG plot from Nexus.

@author: Jussi
"""

from nexus_plot import nexus_plotter
import matplotlib.pyplot as plt

layout = [8,3]
# can get rid of 'X' syntax by checking nplotter.side after OpenTrial
plotvars = ['HipAnglesX','KneeAnglesX','AnkleAnglesX',
            'XHam', 'XRec', 'XTibA',
            'XGlut','XVas','XPer',
            'HipMomentX','KneeMomentX','AnkleMomentX',
            'XRec','XHam','XGas',
            None,'XGlut','XSol',
            None,'XGas',None,
            'HipPowerZ','KneePowerZ','AnklePowerZ']

plotheightratios = [3,2,2,3,2,2,2,3]
pdftitlestr = 'Kinetics_EMG_'

nplotter = nexus_plotter(layout, plotvars)
trialpath='C:\\Users\\HUS20664877\\Desktop\\Vicon\\vicon_data\\test\\D0001AV\\2015_4_23_seur_AV\\'
trial1='2015_4_23_seur_AV14'
trial2='2015_4_23_seur_AV19'
trial3='2015_4_23_seur_AV24'

nplotter.open_trial(trialpath+trial1)
nplotter.plot_trial(plotheightratios=plotheightratios, maintitle='', 
           makepdf=False, onesided_kinematics=True)

nplotter.open_trial(trialpath+trial2)
nplotter.plot_trial(plotheightratios=plotheightratios, maintitle=trial1+' / '+trial2,
           makepdf=False, onesided_kinematics=True,
           linestyle='--', emg_tracecolor='blue')

nplotter.open_trial(trialpath+trial3)
nplotter.plot_trial(plotheightratios=plotheightratios, maintitle=trial1+' / '+trial2+' / '+trial3,
           makepdf=True, onesided_kinematics=True,
           linestyle='-.', emg_tracecolor='gray')

plt.show()
