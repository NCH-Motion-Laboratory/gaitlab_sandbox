# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

Plot Plug-in Gait outputs (online) from Nexus. 
Kinematics and kinetics on separate plots.

@author: Jussi
"""


from gp.plot import gaitplotter
import gp.layouts

plotvars = gp.layouts.std_kinall
maintitleprefix = 'Kinematics/kinetics plot for '
gplotter = gaitplotter()
gplotter.open_nexus_trial()
gplotter.read_trial(plotvars)

gplotter.external_play_video(gplotter.trial.video_files[0])

gplotter.plot_trial(maintitleprefix=maintitleprefix)
gplotter.show()
    



   
