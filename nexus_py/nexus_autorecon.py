# -*- coding: utf-8 -*-
"""
Created on Thu Sep 03 14:54:34 2015

Autorecon + save all trials. Be careful - may overwrite previous
processing.


@author: Jussi
"""

from gp.plot import gaitplotter
import gp.getdata
from gp.getdata import get_eclipse_key
import gp.layouts
import glob
import os

PIPELINE = 'autorecon_and_save'

if not gp.getdata.nexus_pid():
    gp.getdata.error_exit('Vicon Nexus not running')
    
# get session path from Nexus, find processed trials
vicon = gp.getdata.viconnexus()
trialname_ = vicon.GetTrialName()
sessionpath = trialname_[0]
enffiles = glob.glob(sessionpath+'*.enf')

# open each trial and run autorecon pipeline
for filepath_ in enffiles:
    print('processing', filepath_)
    filepath = os.path.splitext(filepath_)[0]  # rm extension
    vicon.OpenTrial(filepath, 45)
    vicon.RunPipeline(PIPELINE,'',45)
    
    