# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

Plot PiG outputs (online) from Nexus.

@author: Jussi
"""

from nexus_plot import nexus_plotter
import matplotlib.pyplot as plt

layout = [4,3]

plotvars = ['PelvisAnglesX',
           'PelvisAnglesY',
           'PelvisAnglesZ',
           'HipAnglesX',
           'HipAnglesY',
           'HipAnglesZ',
           'KneeAnglesX',
           'KneeAnglesY',
           'KneeAnglesZ',
           'AnkleAnglesX',
           'FootProgressAnglesZ',
           'AnkleAnglesZ']
maintitlestr = 'Kinematics plot for '

nplotter = nexus_plotter(layout, plotvars)
nplotter.open_trial()
nplotter.plot_trial(maintitlestr=maintitlestr)

plotvars = ['HipMomentX',
            'HipMomentY',
             'HipMomentZ',
             'HipPowerZ',
             'KneeMomentX',
             'KneeMomentY',
             'KneeMomentZ',
             'KneePowerZ',
             'AnkleMomentX',None,None,
             'AnklePowerZ']                      
maintitlestr = 'Kinetics plot for '

nplotter = nexus_plotter(layout, plotvars)
nplotter.open_trial()
nplotter.plot_trial(maintitlestr=maintitlestr)

plt.show()
    
   
