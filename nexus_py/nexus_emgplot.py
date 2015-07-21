# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:25:38 2015

EMG plot from Nexus.

@author: Jussi
"""

from gait_plot import gaitplotter

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

nplotter = gaitplotter(layout)
nplotter.open_nexus_trial(plotvars)
trialname = nplotter.trialname
maintitle = maintitleprefix + trialname
maintitle = maintitle + '\n' + nplotter.get_emg_filter_description()
nplotter.plot_trial(maintitle=maintitle, onesided_kinematics=True)
nplotter.create_pdf(pdf_prefix=pdftitlestr)

nplotter.show()



