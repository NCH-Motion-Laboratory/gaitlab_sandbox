# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

Plot Plug-in Gait outputs (online) from Nexus. 
Kinematics and kinetics on separate plots.

@author: Jussi
"""


from gp.plot import gaitplotter
import gp.layouts

layout = [4,3]

plotvars = gp.layouts.std_kinematics
maintitleprefix = 'Kinematics plot for '
nplotter = gaitplotter(layout)
nplotter.open_nexus_trial()
nplotter.read_trial(plotvars)
nplotter.plot_trial(maintitleprefix=maintitleprefix)

plotvars = gp.layouts.std_kinetics
maintitleprefix = 'Kinetics plot for '
nplotter = gaitplotter(layout)
nplotter.open_nexus_trial()
nplotter.read_trial(plotvars)
nplotter.plot_trial(maintitleprefix=maintitleprefix)

nplotter.show()
    

   
