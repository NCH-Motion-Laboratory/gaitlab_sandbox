# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:25:38 2015

EMG plot from Nexus.

@author: Jussi
"""

from nexus_plot import nexus_plotter

layout = [8,2]
plotvars = ['RGlut','LGlut',
              'RHam','LHam',
              'RRec','LRec',
              'RVas','LVas',
              'RTibA','LTibA',
              'RPer','LPer',
              'RGas','LGas',
              'RSol','LSol']
maintitleprefix = 'EMG plot for '
pdftitlestr = 'EMG_'

nplotter = nexus_plotter(layout)
nplotter.open_trial(plotvars)
trialname = nplotter.trialname
nplotter.plot_trial(maintitle=maintitleprefix+trialname, onesided_kinematics=True)
nplotter.create_pdf(pdf_prefix=pdftitlestr)

nplotter.show()
