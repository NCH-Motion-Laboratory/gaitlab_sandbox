# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:25:38 2015

EMG plot from c3d file. WIP

@author: Jussi
"""

from nexus_plot import nexus_plotter

c3dfile = "C:/Users/HUS20664877/Desktop/Vicon/vicon_data/test/D0012_VS/2015_6_9_seur_VS/2015_6_9_seur_VS33.c3d"

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
nplotter.open_c3d_trial(plotvars, c3dfile)
trialname = nplotter.trialname
maintitle = maintitleprefix + trialname
maintitle = maintitle + '\n' + nplotter.get_emg_filter_description()
nplotter.plot_trial(maintitle=maintitle, onesided_kinematics=True)
nplotter.create_pdf(pdf_prefix=pdftitlestr)

nplotter.show()



