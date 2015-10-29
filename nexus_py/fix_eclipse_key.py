# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 11:17:45 2015

Utility to clean unwanted Eclipse entries.
Be careful

@author: vicon123
"""


import gp.getdata 
import glob
import sys

KEY = 'DESCRIPTION'
OLDVAL = 'puola'
NEWVAL = 'kuola'
ENF_GLOB = '*Trial*enf'

vicon = gp.getdata.viconnexus()
trialname_ = vicon.GetTrialName()
sessionpath = trialname_[0]
print(sessionpath)
enffiles = glob.glob(sessionpath+ENF_GLOB)

for enffile in enffiles:
    gp.getdata.set_eclipse_key(enffile, KEY, OLDVAL, NEWVAL)
    
    
        


