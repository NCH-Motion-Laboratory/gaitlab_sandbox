# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:25:38 2015

EMG plot from Nexus.

@author: Jussi
"""

from nexus_plot import nexus_plotter
import matplotlib.pyplot as plt

layout = [8,2]
plotvars = ['RGlut','LGlut',
              'RHam','LHam',
              'RRec','LRec',
              'RVas','LVas',
              'RTibA','LTibA',
              'RPer','LPer',
              'RGas','LGas',
              'RSol','LSol']
maintitlestr = 'EMG plot for '
makepdf = True
pdftitlestr = 'EMG_'

nplotter = nexus_plotter(layout, plotvars)
nplotter.open_trial()
nplotter.plot_trial(maintitlestr=maintitlestr, makepdf=makepdf, 
                    pdftitlestr=pdftitlestr, onesided_kinematics=True)

plt.show()
