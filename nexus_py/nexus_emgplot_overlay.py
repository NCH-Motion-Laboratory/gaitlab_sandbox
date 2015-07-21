# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

EMG overlay plot from Nexus. WIP

FIXME: implement dialog to load c3d files from different sessions.

@author: Jussi
"""

from nexus_plot import nexus_plotter
import sys
from nexus_getdata import error_exit

layout = [9,2]
pdftitlestr = 'EMG_'
emgcolors = ['black','blue','gray']
MAX_TRIALS = 3

nplotter = nexus_plotter(layout)
trials = nplotter.trialselector()

# annotating disconnected EMGs messes up overlay plot
nplotter.annotate_disconnected = False

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
    nplotter.open_nexus_trial(trialpath=trial, nexusvars=plotvars)
    maintitle = 'EMG overlay plot' + '\n' + nplotter.get_emg_filter_description()
    nplotter.plot_trial(maintitle=maintitle,
                        emg_tracecolor=emgcolors[i])

#nplotter.set_fig_title('\n'.join(trials))
nplotter.show()
#nplotter.create_pdf(pdf_name='overlay.pdf')

