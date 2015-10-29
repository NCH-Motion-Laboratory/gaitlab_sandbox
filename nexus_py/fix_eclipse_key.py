# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 11:17:45 2015

Utility to fix unwanted Eclipse entries.
Fixes all enf files in current Nexus directory.

Be careful

@author: jussi
"""


import gp.getdata 
import glob
import sys

KEY = 'DESCRIPTION'  # Eclipse key
OLDVAL = 'junk'  # change keys with this value
NEWVAL = ''      # change into this value
ENF_GLOB = '*Trial*enf'

vicon = gp.getdata.viconnexus()
trialname_ = vicon.GetTrialName()
sessionpath = trialname_[0]
print(sessionpath)
enffiles = glob.glob(sessionpath+ENF_GLOB)

for enffile in enffiles:
    gp.getdata.set_eclipse_key(enffile, KEY, OLDVAL, NEWVAL)
    
    
        


