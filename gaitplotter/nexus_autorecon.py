# -*- coding: utf-8 -*-
"""
Created on Thu Sep 03 14:54:34 2015

Autorecon + save all trials. Be careful - may overwrite previous
processing (e.g. labels of static trial)


@author: Jussi
"""

from __future__ import print_function
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
enffiles = glob.glob(sessionpath+'*Trial*.enf')

# open each trial and run autorecon pipeline
for filepath_ in enffiles:
    filepath = os.path.splitext(filepath_)[0]  # rm extension
    filepath = filepath[:filepath.find('.Trial')]  # rm .Trial
    # TODO: extract trial number so that early trials (video+static) can be skipped
    print('processing', filepath)
    vicon.OpenTrial(filepath, 45)
    vicon.RunPipeline(PIPELINE,'',45)
    
    