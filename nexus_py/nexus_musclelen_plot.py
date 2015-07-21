# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

Muscle length plot.

@author: Jussi
"""


 
 
 
from gait_plot import gaitplotter

layout = [3,3]

maintitleprefix='Muscle length plot for '

nplotter = gaitplotter(layout)

plotvars = ['PsoaLength', 'GracLength', 'ReFeLength',
            'BiFLLength', 'SeTeLength', 'SeMeLength',
            'MeGaLength', 'LaGaLength', 'SoleLength']

nplotter.open_nexus_trial(nexusvars=plotvars)

trialname = nplotter.trialname
maintitle = maintitleprefix + trialname

nplotter.plot_trial(maintitle=maintitle)

nplotter.show()





