# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

EMG overlay plot from c3d files. WIP


@author: Jussi
"""

from gait_plot import gaitplotter
import sys
from gait_getdata import error_exit

layout = [9,2]
pdftitlestr = 'EMG_'
emgcolors = ['black','blue','gray']
MAX_TRIALS = 3

plotter = gaitplotter(layout)
trials = plotter.trialselector()

# annotating disconnected EMGs messes up overlay plot
plotter.annotate_disconnected = False

if trials == None:
    sys.exit()
    
if len(trials) > MAX_TRIALS:
    error_exit('Too many trials selected for the overlay plot!')

plotvars = ['RGlut','LGlut',
          'RHam','LHam',
          'RRec','LRec',
          'RVas','LVas',
          'RTibA','LTibA',
          'RPer','LPer',
          'RGas','LGas',
          'RSol','LSol',
          'emglegend',None]

for i,trial in enumerate(trials):
    # open again and read vars now
    plotter.open_nexus_trial(trialpath=trial, vars=plotvars)
    maintitle = 'EMG overlay plot' + '\n' + plotter.get_emg_filter_description()
    plotter.plot_trial(maintitle=maintitle,
                        emg_tracecolor=emgcolors[i])

#plotter.set_fig_title('\n'.join(trials))
plotter.show()
#plotter.create_pdf(pdf_name='overlay.pdf')

