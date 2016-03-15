# -*- coding: utf-8 -*-
"""
Created on Tue Apr 28 11:37:51 2015

Kinematics only -EMG plot from Nexus (no kinetics) + PDF.
L/R sides on separate plots.
If no EMG, do one page kinematics/kinetics instead.

@author: Jussi
"""

 
from gp.plot import gaitplotter
import gp.layouts

def do_plot(emg=True):
    
    gplotter = gaitplotter()
    gplotter.open_nexus_trial()
    trialname = gplotter.trial.trialname

    if emg:
        plotheightratios = [3,2,2,2,2,2]
        pdf_prefix = 'Kinematics_EMG_'
        maintitleprefix='Kinematics-EMG plot for '
        for side in ['L', 'R']:
            plotvars = gp.layouts.kinematics_emg(side)
            gplotter.read_trial(plotvars)
            maintitle = maintitleprefix + trialname + ' ('+side+')'
            maintitle = maintitle + '\n' + gplotter.get_emg_filter_description()
            gplotter.plot_trial(plotheightratios=plotheightratios, maintitle=maintitle)
            gplotter.create_pdf(pdf_name=pdf_prefix+trialname+'_'+side+'.pdf')
            gplotter.show()
            
    else:
        plotvars = gp.layouts.std_kinematics
        pdf_prefix = 'Kinematics_kinetics_'
        maintitleprefix = 'Kinematics/kinetics plot for '
        maintitle = maintitleprefix + trialname
        gplotter.read_trial(plotvars)
        gplotter.plot_trial(maintitle=maintitle)
        gplotter.create_pdf(pdf_name=pdf_prefix+trialname+'.pdf')
        gplotter.show()


if __name__ == '__main__':
    do_plot(emg=False)
    
    
