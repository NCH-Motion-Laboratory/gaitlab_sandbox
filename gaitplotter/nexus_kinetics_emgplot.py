# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

Kinetics-EMG plot from Nexus.
If no EMG data, kinetics/kinematics plot instead.

@author: Jussi
"""

 
from gp.plot import gaitplotter
import gp.layouts

gplotter = gaitplotter()

def do_plot(emg=True):

    # need to open trial before detecting side
    gplotter.open_nexus_trial()
    side = gplotter.trial.kinetics_side
    if emg:
        plotvars = gp.layouts.kinetics_emg(side)
        plotheightratios = [3,2,2,3,2,2,2,3]
        pdf_prefix = 'Kinetics_EMG_'
        maintitleprefix='Kinetics-EMG plot for '
    else:
        plotvars = gp.layouts.std_kinall
        plotheightratios = None
        pdf_prefix = 'Kinetics_kinematics_'
        maintitleprefix='Kinetics/kinematics plot for '
    
    # choose EMG variables according to side
    gplotter.read_trial(plotvars)
    
    trialname = gplotter.trial.trialname
    maintitle = maintitleprefix + trialname
    if emg:
        maintitle = maintitle + '\n' + gplotter.get_emg_filter_description()
    
    gplotter.plot_trial(plotheightratios=plotheightratios, maintitle=maintitle)
    gplotter.create_pdf(pdf_prefix=pdf_prefix)
   
    gplotter.show()

if __name__ == '__main__':
    do_plot(emg=False)
    

