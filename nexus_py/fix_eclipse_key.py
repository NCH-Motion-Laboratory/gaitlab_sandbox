# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 11:17:45 2015

Utility to clean unwanted Eclipse entries.

@author: vicon123
"""

import gp.getdata 
import glob
import sys

KEY = 'DESCRIPTION'
OLDVAL = 'unipedal right'
NEWVAL = ''

vicon = gp.getdata.viconnexus()
trialname_ = vicon.GetTrialName()
sessionpath = trialname_[0]
print(sessionpath)
enffiles = glob.glob(sessionpath+'*.enf')

for enffile in enffiles:
    print('\n'+enffile+'\n')
    gp.getdata.set_eclipse_key(enffile, KEY, OLDVAL, NEWVAL)
    
    
        


