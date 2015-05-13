# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

Kinematics-EMG overlay plot from Nexus.
Work in progress

@author: Jussi
"""

from nexus_plot import nexus_plotter
import sys
from nexus_getdata import error_exit

layout = [8,3]
plotheightratios = [3,2,2,3,2,2,2,3]
pdftitlestr = 'Kinetics_EMG_'
pigstyles = ['-','--','-.']
emgcolors = ['black','blue','gray']
MAX_TRIALS = 3

nplotter = nexus_plotter(layout)
trials = nplotter.trialselector()

# annotating disconnected EMGs messes up overlay plot
nplotter.annotate_disconnected = False

nplotter.totalfigsize = (16,12)

if trials == None:
    sys.exit()
    
if len(trials) > MAX_TRIALS:
    error_exit('Too many trials selected for the overlay plot!')

for i,trial in enumerate(trials):
    # need to open trial to detect side (don't read variables yet)
    nplotter.open_trial(trialpath=trial, nexusvars=None)
    side = nplotter.side
    # then choose EMG variables according to side
    plotvars = ['HipAnglesX','KneeAnglesX','AnkleAnglesX',
                side+'Ham', side+'Rec', side+'TibA',
                side+'Glut',side+'Vas',side+'Per',
                'HipMomentX','KneeMomentX','AnkleMomentX',
                side+'Rec',side+'Ham',side+'Gas',
                'emglegend',side+'Glut',side+'Sol',
                'piglegend',side+'Gas',None,
                'HipPowerZ','KneePowerZ','AnklePowerZ']
    # open again and read vars now
    nplotter.open_trial(trialpath=trial, nexusvars=plotvars)
    nplotter.plot_trial(plotheightratios=plotheightratios, maintitle='Kinetics-EMG overlay plot',
                        onesided_kinematics=False, pig_linestyle=pigstyles[i],
                        emg_tracecolor=emgcolors[i])

#nplotter.set_fig_title('\n'.join(trials))
nplotter.show()
#nplotter.create_pdf(pdf_name='overlay.pdf')

