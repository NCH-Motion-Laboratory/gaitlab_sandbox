# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

Kinematics-EMG plot from Nexus.

@author: Jussi
"""

from nexus_plot import nexus_plotter
import sys
from nexus_getdata import error_exit

layout = [8,3]
plotheightratios = [3,2,2,3,2,2,2,3]
pdftitlestr = 'Kinetics_EMG_'
MAX_TRIALS = 5

nplotter = nexus_plotter(layout)
trials = nplotter.trialselector()

if trials == None:
    sys.exit()
    
if len(trials) > MAX_TRIALS:
    error_exit('Too many trials selected for the overlay plot!')

for trial in trials:
    # need to open trial before detecting side
    nplotter.open_trial(trialpath=trial, nexusvars=None)
    side = nplotter.detect_side()
    # choose EMG variables according to side
    plotvars = ['HipAnglesX','KneeAnglesX','AnkleAnglesX',
                side+'Ham', side+'Rec', side+'TibA',
                side+'Glut',side+'Vas',side+'Per',
                'HipMomentX','KneeMomentX','AnkleMomentX',
                side+'Rec',side+'Ham',side+'Gas',
                None,side+'Glut',side+'Sol',
                None,side+'Gas',None,
                'HipPowerZ','KneePowerZ','AnklePowerZ']
    print('Opening: ', trial)
    nplotter.open_trial(trialpath=trial, nexusvars=plotvars)
    nplotter.plot_trial(plotheightratios=plotheightratios, maintitle='',
                        onesided_kinematics=True)

nplotter.set_fig_title('\n'.join(trials))
nplotter.show()
nplotter.create_pdf(pdf_name='test.pdf')

