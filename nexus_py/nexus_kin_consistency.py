# -*- coding: utf-8 -*-
"""
Created on Thu Sep 03 14:54:34 2015

EMG consistency plot from Nexus. Automatically picks trials based on Eclipse
description and defined search strings.

@author: Jussi
"""

from gp.plot import gaitplotter
import gp.getdata
from gp.getdata import get_eclipse_key
import gp.layouts
import glob

def any_substr(str, substrs):
    """ Find whether str contains one of substr (list). """
    if str:
        return any(substr in str for substr in substrs)
    else:
        return None

MAX_TRIALS = 6

if not gp.getdata.nexus_pid():
    gp.getdata.error_exit('Vicon Nexus not running')
    
# get session path from Nexus, find processed trials
vicon = gp.getdata.viconnexus()
trialname_ = vicon.GetTrialName()
sessionpath = trialname_[0]
c3dfiles = glob.glob(sessionpath+'*.c3d')

# Eclipse trial notes/description must contain one of these strings
marks = ['R1','R2','R3','L1','L2','L3']

marked_trials = [c3d for c3d in c3dfiles if any_substr(get_eclipse_key(c3d, 'DESCRIPTION').upper()+' '+get_eclipse_key(c3d, 'NOTES').upper(), marks)]
if len(marked_trials) > MAX_TRIALS:
    gp.getdata.error_exit('Too many marked trials found!')

if not marked_trials:
    gp.getdata.error_exit('Did not find any marked trials (R1 etc.) in current session directory.')

plotvars = gp.layouts.overlay_kinall

gplotter = gaitplotter()
maintitle = 'Kinematics/kinetics consistency plot'

for i,trialpath in enumerate(marked_trials):
    gplotter.open_c3d_trial(trialpath)
    gplotter.read_trial(plotvars)
    gplotter.plot_trial(maintitle=maintitle)
    
gplotter.show()
gplotter.create_pdf('kin_consistency.pdf')

    