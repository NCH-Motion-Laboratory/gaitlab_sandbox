# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

single emg plot from c3d

@author: Jussi
"""

from gp.plot import gaitplotter
import gp.layouts

plotvars = gp.layouts.std_emg

trialpath = "C:/Users/HUS20664877/Desktop/Vicon/vicon_data/test/Verrokki10v_OK/2015_10_12_boy10v_OK/2015_10_12_boy10v_OK09.c3d"

gplotter = gaitplotter()
gplotter.open_c3d_trial(trialpath)
gplotter.read_trial(plotvars)
maintitle = 'EMG plot for ' + gplotter.trial.trialname + '\n' + gplotter.get_emg_filter_description()
gplotter.plot_trial(maintitle=maintitle)
   
gplotter.show()

