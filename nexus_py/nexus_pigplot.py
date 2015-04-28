# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

Plot PiG outputs (online) from Nexus.

@author: Jussi
"""

from nexus_plot import nexus_plot

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
plotheightratios = [2]*4
maintitlestr = 'Kinematics plot for '
makepdf = False

nexus_plot(layout, plotvars, plotheightratios, maintitlestr, makepdf)
    
   
layout = [4,3]
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
           
plotheightratios = [2]*4
maintitlestr = 'Kinetics plot for '
makepdf = False

nexus_plot(layout, plotvars, plotheightratios, maintitlestr, makepdf)
    
    
